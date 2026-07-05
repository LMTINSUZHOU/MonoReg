from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class PublicRegistrationCreate(BaseModel):
    name: str | None = None
    email: EmailStr
    phone: str | None = None
    form_data: dict[str, Any] = Field(default_factory=dict)


class RegistrationUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    status: str | None = None
    form_data: dict[str, Any] | None = None


class BatchStatusUpdate(BaseModel):
    registration_ids: list[int]
    status: str


class RegistrationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activity_id: int
    name: str | None = None
    email: EmailStr
    phone: str | None = None
    status: str
    form_data: dict[str, Any]
    submitted_ip: str | None = None
    user_agent: str | None = None
    submitted_at: datetime
    updated_at: datetime

