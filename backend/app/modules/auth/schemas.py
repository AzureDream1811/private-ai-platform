from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def validate_password_bytes(value: str) -> str:
    if not value:
        raise ValueError("Password cannot be empty")

    if len(value.encode("utf-8")) > 72:
        raise ValueError("Password cannot exceed 72 bytes")

    return value


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

    _validate_password = field_validator("password")(validate_password_bytes)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    _validate_password = field_validator("password")(validate_password_bytes)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    created_at: datetime

class RegisterResponse(BaseModel):
    user: UserResponse

class LoginResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse
