from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.security import hash_refresh_token
from backend.app.database.models.refresh_token import RefreshToken
from backend.app.database.models.user import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    return db.scalar(stmt)

def get_user_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt)


def get_user_by_username(db: Session, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    return db.scalar(stmt)


def create_user(db: Session, username: str, email: str, password_hash: str) -> User:
    new_user = User(username=username, email=email, password_hash=password_hash)
    db.add(new_user)
    db.flush()
    return new_user


def create_refresh_token_record(
    db: Session, user_id: int, refresh_token: str, expires_at: datetime
) -> RefreshToken:
    hashed_token = hash_refresh_token(refresh_token)
    new_refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=hashed_token,
        expires_at=expires_at,
    )
    db.add(new_refresh_token)
    db.flush()

    return new_refresh_token


def get_refresh_token_by_hash(db: Session, token_hash: str) -> RefreshToken | None:
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)

    refresh_token = db.scalar(stmt)

    now = datetime.now(UTC)

    if not refresh_token:
        return None

    if refresh_token.revoked_at is not None or refresh_token.expires_at <= now:
        return None

    return refresh_token


def revoke_refresh_token(refresh_token: RefreshToken) -> None:
    refresh_token.revoked_at = datetime.now(UTC)
