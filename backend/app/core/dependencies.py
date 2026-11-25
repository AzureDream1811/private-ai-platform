from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.app.core.security import decode_token
from backend.app.database.models.user import User
from backend.app.database.session import get_db
from backend.app.modules.auth.repository import get_user_by_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

DBSession = Annotated[Session, Depends(get_db)]
Token = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(token: Token, db: DBSession) -> User:
    try:
        decoded_token = decode_token(token, expected_type="access")
        user_id = int(decoded_token["sub"])
        user = get_user_by_id(db, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
