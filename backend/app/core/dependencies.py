from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.app.core.security import decode_token
from backend.app.database.models.enum import UserRole
from backend.app.database.models.user import User
from backend.app.database.session import get_db
from backend.app.modules.auth.repository import get_user_by_id

http_bearer = HTTPBearer()

DBSession = Annotated[Session, Depends(get_db)]
Token = Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]


def _unauthorized_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: Token, db: DBSession) -> User:
    try:
        decoded_token = decode_token(token.credentials, expected_type="access")
        user_id = int(decoded_token["sub"])

    except (jwt.PyJWTError, KeyError, ValueError, TypeError) as e:
        raise _unauthorized_exception() from e

    user = get_user_by_id(db, user_id)

    if user is None:
        raise _unauthorized_exception()

    return user


def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action.",
        )
    return current_user
