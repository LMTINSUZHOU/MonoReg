from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ActivityBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    slug: str = Field(min_length=1, max_length=128)
    description: str | None = None
    status: str = "draft"
    start_time: datetime | None = None
    end_time: datetime | None = None
    max_registrations: int | None = None
    need_account: bool = False
    auto_generate_account: bool = False
    send_confirm_email: bool = False
    send_account_email_immediately: bool = False
    login_url: str | None = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=255)
    slug: str | None = Field(default=None, max_length=128)
    description: str | None = None
    status: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    max_registrations: int | None = None
    need_account: bool | None = None
    auto_generate_account: bool | None = None
    send_confirm_email: bool | None = None
    send_account_email_immediately: bool | None = None
    login_url: str | None = None


class ActivityOut(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by: int | None = None
    created_at: datetime
    updated_at: datetime

