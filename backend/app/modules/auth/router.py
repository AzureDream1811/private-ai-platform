from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.dependencies import get_current_user
from backend.app.database.models.user import User
from backend.app.database.session import get_db
from backend.app.modules.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    UserResponse,
)
from backend.app.modules.auth.service import (
    login,
    logout,
    refresh_access_token,
    register,
)

router = APIRouter()
DBSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post(
    "/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED
)
def register_user(request: RegisterRequest, db: DBSession):
    try:
        return register(db, request.username, request.email, request.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login_user(request: LoginRequest, db: DBSession):
    try:
        return login(db, request.email, request.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/refresh", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def refresh_token(request: RefreshRequest, db: DBSession):
    try:
        return refresh_access_token(db, request.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout_user(request: RefreshRequest, db: DBSession):
    try:
        logout(db, request.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_me(current_user: CurrentUser):
    return current_user
