from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from bcrypt import checkpw, gensalt, hashpw

from backend.app.core.config import settings


def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) <= 0:
        raise ValueError("Password can not be empty")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password cannot exceed 72 bytes")

    return str(hashpw(password.encode("utf-8"), salt=gensalt()), "utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    if len(password.encode("utf-8")) <= 0:
        raise ValueError("Password can not be empty")

    if len(password.encode("utf-8")) > 72:
        raise ValueError("Password cannot exceed 72 bytes")

    return checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    current_time = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": current_time,
        "exp": current_time + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "jti": str(uuid4()),
        "type": "access",
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def create_refresh_token(user_id: int) -> str:
    current_time = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": current_time,
        "exp": current_time + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "jti": str(uuid4()),
        "type": "refresh",
    }
    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str, expected_type: str) -> dict:
    if expected_type not in ["access", "refresh"]:
        raise ValueError("Invalid expected token type")

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["sub", "iat", "exp", "jti", "type"]},
        )

        if not isinstance(payload["jti"], str) or not payload["jti"]:
            raise ValueError("Invalid token ID")

        if (
            payload["type"] not in ["access", "refresh"]
            or payload["type"] != expected_type
        ):
            raise ValueError("Invalid token type")

        subject = payload.get("sub")

        if not isinstance(subject, str) or not subject.isdigit() or int(subject) <= 0:
            raise ValueError("Invalid user ID in token")

        return payload

    except jwt.ExpiredSignatureError as exc:
        raise ValueError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise ValueError("Invalid token") from exc
