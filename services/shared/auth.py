import os

from fastapi import Header, HTTPException
from jose import JWTError, jwt


secret_key = os.getenv("JWT_SECRET", "local-development-secret")
algorithm = "HS256"


def get_current_user_id(authorization: str = Header(default="")):
    if not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Please log in first")

    token = authorization.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired login session")
