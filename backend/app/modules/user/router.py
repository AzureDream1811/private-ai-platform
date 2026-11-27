from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_admin_user, get_current_user
from backend.app.database.models.user import User
from backend.app.database.session import get_db
from backend.app.modules.user.schemas import (
    AdminUserResponse,
    Page,
    UpdateUserRequest,
    UpdateUserRoleRequest,
)
from backend.app.modules.user.service import (
    get_all_users,
    get_profile,
    get_user_details,
    update_profile,
    update_user_role,
)

router = APIRouter()
DBSession = Annotated[Session, Depends(get_db)]
current_user = Annotated[User, Depends(get_current_user)]


@router.get("/me")
def get_current_user_profile(db: DBSession, current_user: current_user):

    return get_profile(db, current_user.id)


@router.patch("/me")
def update_current_user_profile(
    db: DBSession, current_user: current_user, request: UpdateUserRequest
):

    return update_profile(
        db, current_user.id, request.username, request.email, request.password
    )


@router.get("/{user_id}", dependencies=[Depends(get_current_admin_user)])
def admin_get_user_profile(db: DBSession, user_id: int):
    return get_user_details(db, user_id)


@router.get("/", dependencies=[Depends(get_current_admin_user)])
def admin_list_users(
    db: DBSession, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)
) -> Page[AdminUserResponse]:
    return get_all_users(db, page, size)


@router.patch("/{user_id}", dependencies=[Depends(get_current_admin_user)])
def admin_update_user_role(db: DBSession, user_id: int, request: UpdateUserRoleRequest):
    return update_user_role(db, user_id, request.role)
