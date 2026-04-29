import os
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, HTTPException
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from shared.database import run_database_command
from shared.metrics import MetricsMiddleware, metrics_response


service_name = "auth-service"
secret_key = os.getenv("JWT_SECRET", "local-development-secret")
algorithm = "HS256"
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="Authentication Service")
app.add_middleware(MetricsMiddleware, service_name=service_name)


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    full_name: str
    email: str
    password: str


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


def seed_default_user():
    password_hash = password_context.hash("password123")
    run_database_command(
        """
        INSERT INTO users (full_name, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (email) DO NOTHING
        """,
        ("Miras Aliyev", "miras@example.com", password_hash, "customer"),
    )


@app.on_event("startup")
def prepare_database():
    create_user_table()
    seed_default_user()


@app.get("/health")
def get_health_status():
    return {"service": service_name, "status": "healthy"}


@app.post("/login")
def login_user(login_request: LoginRequest):
    user = run_database_command(
        "SELECT id, full_name, email, password_hash, role FROM users WHERE email = %s",
        (login_request.email,),
        fetch_one=True,
    )
    if not user or not password_context.verify(login_request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    expiration_time = datetime.now(timezone.utc) + timedelta(hours=2)
    token = jwt.encode(
        {
            "sub": str(user["id"]),
            "email": user["email"],
            "role": user["role"],
            "exp": expiration_time,
        },
        secret_key,
        algorithm=algorithm,
    )
    return {"access_token": token, "token_type": "bearer", "user": {"id": user["id"], "full_name": user["full_name"], "email": user["email"], "role": user["role"]}}


@app.post("/register")
def register_user(register_request: RegisterRequest):
    existing_user = run_database_command(
        "SELECT id FROM users WHERE email = %s",
        (register_request.email,),
        fetch_one=True,
    )
    if existing_user:
        raise HTTPException(status_code=409, detail="User with this email already exists")

    password_hash = password_context.hash(register_request.password)
    created_user = run_database_command(
        """
        INSERT INTO users (full_name, email, password_hash, role)
        VALUES (%s, %s, %s, %s)
        RETURNING id, full_name, email, role
        """,
        (register_request.full_name, register_request.email, password_hash, "customer"),
        fetch_one=True,
    )
    return {"message": "Registration successful", "user": created_user}


@app.get("/metrics")
def get_metrics():
    return metrics_response()
