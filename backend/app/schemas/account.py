from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AccountGenerateRequest(BaseModel):
    activity_id: int
    registration_ids: list[int]
    prefix: str = ""
    start_number: int = 1
    digits: int = 4
    password_length: int = 12
    avoid_ambiguous_chars: bool = True
    overwrite: bool = False


class AccountResetPasswordRequest(BaseModel):
    account_ids: list[int]
    password_length: int = 12
    avoid_ambiguous_chars: bool = True


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activity_id: int
    registration_id: int
    username: str
    status: str
    generated_by: int | None = None
    sent_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

