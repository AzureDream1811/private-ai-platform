from datetime import datetime

from pydantic import BaseModel

from backend.app.database.models.enum import UserRole


class UserResponse(BaseModel):
    model_config = {
        "from_attributes": True,
    }

    id: int
    username: str
    email: str
    created_at: datetime


class AdminUserResponse(UserResponse):
    role: str


class UpdateUserRequest(BaseModel):
    model_config = {
        "from_attributes": True,
    }

    username: str | None = None
    email: str | None = None
    password: str | None = None


class UpdateUserRoleRequest(BaseModel):
    model_config = {
        "from_attributes": True,
    }

    role: UserRole
