from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class LoginRequest(BaseModel):
    username: str
    password: str


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr
    role: str
    status: str
    last_login_at: datetime | None = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AdminUserOut

