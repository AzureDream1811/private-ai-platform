from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.security import hash_password
from backend.app.database.models.enum import UserRole
from backend.app.database.models.user import User
from backend.app.modules.user.repository import (
    get_user_by_id,
    get_users,
    is_email_unique,
    is_username_unique,
)
from backend.app.modules.user.schemas import AdminUserResponse, UserResponse


def _commit_and_refresh(db: Session, obj: User) -> None:
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(obj)


def get_profile(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError(f"User with id {user_id} does not exist.")

    return UserResponse.model_validate(user)


def update_profile(
    db: Session,
    user_id: int,
    new_username: str | None = None,
    new_email: str | None = None,
    new_password: str | None = None,
):
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError(f"User with id {user_id} does not exist.")

    if new_username is not None:
        user.username = _update_criteria(user.username, new_username, "Username", is_username_unique)
    if new_email is not None:
        user.email = _update_criteria(user.email, new_email, "Email", is_email_unique)
    if new_password is not None:
        password_hash = hash_password(new_password)
        user.password_hash = password_hash

    user.updated_at = func.now()
    _commit_and_refresh(db, user)

    return UserResponse.model_validate(user)


def _update_criteria(
    current_value: str,
    new_value: str,
    field_name: str,
    is_unique_func,
) -> str:
    new_value = new_value.strip()

    if not new_value:
        raise ValueError(f"{field_name} cannot be empty.")

    if new_value == current_value:
        return current_value

    if not is_unique_func(new_value):
        raise ValueError(f"{field_name} is already in use.")

    return new_value


def admin_get_user_details(db: Session, user_id: int):
    user = get_user_by_id(db, user_id)
    if not user:
        raise ValueError(f"User with id {user_id} does not exist.")

    return AdminUserResponse.model_validate(user)


def admin_get_all_users(db: Session, page: int, size: int):
    users, total = get_users(db, page, size)

    user_admin_responses = [AdminUserResponse.model_validate(user) for user in users]

    return user_admin_responses, total


def admin_update_user_role(db: Session, user_id: int, new_role: UserRole):
    user = get_user_by_id(db, user_id)

    if not user:
        raise ValueError(f"User with id {user_id} does not exist.")

    if user.role == UserRole.ADMIN and new_role != UserRole.ADMIN:
        raise ValueError("Cannot change role of an admin user to a non-admin role.")

    user.role = new_role
    user.updated_at = func.now()
    _commit_and_refresh(db, user)

    return AdminUserResponse.model_validate(user)
