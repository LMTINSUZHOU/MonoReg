from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class EmailTemplateCreate(BaseModel):
    activity_id: int | None = None
    name: str
    type: str
    subject: str
    body: str
    enabled: bool = True


class EmailTemplateUpdate(BaseModel):
    activity_id: int | None = None
    name: str | None = None
    type: str | None = None
    subject: str | None = None
    body: str | None = None
    enabled: bool | None = None


class EmailTemplateOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activity_id: int | None = None
    name: str
    type: str
    subject: str
    body: str
    enabled: bool
    created_at: datetime
    updated_at: datetime


class TemplatePreviewRequest(BaseModel):
    registration_id: int | None = None


class SendTestEmailRequest(BaseModel):
    template_id: int
    to_email: EmailStr
    registration_id: int | None = None


class SendBatchEmailRequest(BaseModel):
    activity_id: int
    template_id: int
    registration_ids: list[int]
    skip_sent: bool = True


class EmailLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int | None = None
    activity_id: int
    registration_id: int | None = None
    to_email: EmailStr
    subject: str
    body_snapshot: str | None = None
    status: str
    error_message: str | None = None
    retry_count: int
    sent_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class EmailJobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activity_id: int
    template_id: int | None = None
    job_type: str
    status: str
    total_count: int
    success_count: int
    failed_count: int
    created_by: int | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

