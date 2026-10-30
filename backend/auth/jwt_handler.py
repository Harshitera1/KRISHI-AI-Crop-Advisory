import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv

load_dotenv()

def _secret_key():
    return os.getenv("SECRET_KEY")


def generate_token(user_id):
    secret_key = _secret_key()
    if not secret_key:
        raise RuntimeError("SECRET_KEY is not configured")
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=12),
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    if isinstance(token, bytes):
        return token.decode("utf-8")
    return token


def verify_token(token):
    secret_key = _secret_key()
    if not secret_key:
        return None
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        if not payload.get("user_id"):
            return None
        return payload
    except (jwt.PyJWTError, TypeError):
        return None
