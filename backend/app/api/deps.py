from collections.abc import Generator

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import AdminUser


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def db_session() -> Generator[Session, None, None]:
    yield from get_db()


def get_current_user(
    db: Session = Depends(db_session),
    token: str = Depends(oauth2_scheme),
) -> AdminUser:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = int(payload.get("sub"))
    except (jwt.PyJWTError, TypeError, ValueError) as exc:
        raise credentials_error from exc
    user = db.get(AdminUser, user_id)
    if not user or user.status != "active":
        raise credentials_error
    return user


def require_write_user(user: AdminUser = Depends(get_current_user)) -> AdminUser:
    if user.role == "viewer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="viewer 无写入权限")
    return user

