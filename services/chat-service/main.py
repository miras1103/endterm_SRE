from fastapi import Depends, FastAPI
from pydantic import BaseModel

from shared.auth import get_current_user_id
from shared.database import run_database_command
from shared.metrics import MetricsMiddleware, metrics_response


service_name = "chat-service"
app = FastAPI(title="Chat Service")
app.add_middleware(MetricsMiddleware, service_name=service_name)


class ChatMessageRequest(BaseModel):
    receiver_id: int
    message_text: str


@app.on_event("startup")
def prepare_database():
    run_database_command(
        """
        CREATE TABLE IF NOT EXISTS chat_messages (
            id SERIAL PRIMARY KEY,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            message_text TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
        """
    )


@app.get("/health")
def get_health_status():
    return {"service": service_name, "status": "healthy"}


@app.get("/messages")
def list_messages(current_user_id: int = Depends(get_current_user_id)):
    messages = run_database_command(
        """
        SELECT id, sender_id, receiver_id, message_text, created_at
        FROM chat_messages
        WHERE sender_id = %s OR receiver_id = %s
        ORDER BY id DESC
        """,
        (current_user_id, current_user_id),
        fetch_all=True,
    )
    return {"messages": messages}


@app.post("/messages")
def create_message(message_request: ChatMessageRequest, current_user_id: int = Depends(get_current_user_id)):
    message = run_database_command(
        """
        INSERT INTO chat_messages (sender_id, receiver_id, message_text)
        VALUES (%s, %s, %s)
        RETURNING id, sender_id, receiver_id, message_text, created_at
        """,
        (
            current_user_id,
            message_request.receiver_id,
            message_request.message_text,
        ),
        fetch_one=True,
    )
    return message


@app.get("/metrics")
def get_metrics():
    return metrics_response()
