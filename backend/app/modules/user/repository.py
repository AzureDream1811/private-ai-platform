

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.database.models.user import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    return db.scalar(stmt)

def is_username_unique(db: Session, username: str) -> bool:
    stmt = select(User).where(User.username == username)
    return db.scalar(stmt) is None

def is_email_unique(db: Session, email: str) -> bool:
    stmt = select(User).where(User.email == email)
    return db.scalar(stmt) is None 

def get_users(db: Session, page: int, size: int) -> tuple[list[User], int]:
    stmt = select(User)
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(
        stmt.order_by(User.id).offset((page - 1) * size).limit(size)
    ).all()

    return list(items), total