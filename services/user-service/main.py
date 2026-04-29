from fastapi import FastAPI
from pydantic import BaseModel

from shared.database import run_database_command
from shared.metrics import MetricsMiddleware, metrics_response


service_name = "user-service"
app = FastAPI(title="User Service")
app.add_middleware(MetricsMiddleware, service_name=service_name)


class UserCreateRequest(BaseModel):
    full_name: str
    email: str
    password_hash: str
    role: str = "customer"


@app.on_event("startup")
def create_user_table():
    run_database_command(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'customer'
        )
        """
    )


@app.get("/health")
def get_health_status():
    return {"service": service_name, "status": "healthy"}


@app.get("/users")
def list_users():
    users = run_database_command(
        "SELECT id, full_name, email, role FROM users ORDER BY id",
        fetch_all=True,
    )
    return {"users": users}


@app.post("/users")
def create_user(user_request: UserCreateRequest):
    created_user = run_database_command(
        """
        INSERT INTO users (full_name, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
        RETURNING id, full_name, email, role
        """,
        (user_request.full_name, user_request.email, user_request.password_hash, user_request.role),
        fetch_one=True,
    )
    return created_user


@app.get("/metrics")
def get_metrics():
    return metrics_response()
