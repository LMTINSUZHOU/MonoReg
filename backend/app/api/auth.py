from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.core.security import create_access_token, verify_password
from app.models import AdminUser
from app.schemas.auth import LoginRequest
from app.schemas.common import ok

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(db_session)):
    user = db.execute(select(AdminUser).where(AdminUser.username == payload.username)).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash) or user.status != "active":
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    user.last_login_at = datetime.now()
    db.commit()
    db.refresh(user)
    return ok(
        {
            "access_token": create_access_token(user.id),
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "status": user.status,
            },
        }
    )


@router.get("/me")
def me(user: AdminUser = Depends(get_current_user)):
    return ok(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status,
            "last_login_at": user.last_login_at,
        }
    )

