from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from backend.app.modules.auth.repository import (
    create_refresh_token_record,
    create_user,
    get_refresh_token_by_hash,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    revoke_refresh_token,
)
from backend.app.modules.auth.schemas import LoginResponse, RegisterResponse


def register(db: Session, username: str, email: str, password: str) -> RegisterResponse:
    if get_user_by_email(db, email):
        raise ValueError("Email is already taken")

    if get_user_by_username(db, username):
        raise ValueError("Username is already taken")

    try:
        password_hash = hash_password(password)
        user = create_user(db, username, email, password_hash)

        response = RegisterResponse.model_validate({"user": user})

        db.commit()
        return response

    except Exception:
        db.rollback()
        raise


def login(db: Session, email: str, password: str) -> LoginResponse:
    user = get_user_by_email(db, email)

    if not user or not verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password")

    try:
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        decoded_token = decode_token(refresh_token, expected_type="refresh")

        expires_at = datetime.fromtimestamp(decoded_token["exp"], tz=UTC)

        create_refresh_token_record(db, user.id, refresh_token, expires_at)

        response = LoginResponse.model_validate(
            {
                "user": user,
                "tokens": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                },
            }
        )

        db.commit()
        return response

    except Exception:
        db.rollback()
        raise


def refresh_access_token(db: Session, refresh_token: str) -> LoginResponse:
    try:
        # Decode the refresh token and verify its validity
        decoded_token = decode_token(refresh_token, expected_type="refresh")

        # Find token in database
        token_hash = hash_refresh_token(refresh_token)
        token_record = get_refresh_token_by_hash(db, token_hash)

        if not token_record:
            raise ValueError("Invalid or expired refresh token")

        user_id = int(decoded_token["sub"])

        if token_record.user_id != user_id:
            raise ValueError("Refresh token does not belong to the user")

        # Get User
        user = get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        # Revoke the old refresh token
        revoke_refresh_token(token_record)

        # Create new access and refresh tokens
        new_access_token = create_access_token(user_id)
        new_refresh_token = create_refresh_token(user_id)

        # Get new token expiration time
        decoded_token = decode_token(new_refresh_token, expected_type="refresh")
        expires_at = datetime.fromtimestamp(decoded_token["exp"], tz=UTC)

        # Store the new refresh token in the database
        create_refresh_token_record(db, user_id, new_refresh_token, expires_at)

        # Return the new tokens and user information
        response = {
            "user": user,
            "tokens": {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
            },
        }

        db.commit()
        return LoginResponse.model_validate(response)
    
    except Exception:
        db.rollback()
        raise

def logout(db: Session, refresh_token: str) -> None:
    try:
        # Decode the refresh token and verify its validity
        decoded_token = decode_token(refresh_token, expected_type="refresh")

        # Find token in database
        token_hash = hash_refresh_token(refresh_token)
        token_record = get_refresh_token_by_hash(db, token_hash)

        if not token_record:
            raise ValueError("Invalid or expired refresh token")

        user_id = int(decoded_token["sub"])

        if token_record.user_id != user_id:
            raise ValueError("Refresh token does not belong to the user")

        # Revoke the refresh token
        revoke_refresh_token(token_record)

        db.commit()

    except Exception:
        db.rollback()
        raise
