from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FormFieldBase(BaseModel):
    field_key: str = Field(min_length=1, max_length=128)
    field_label: str = Field(min_length=1, max_length=255)
    field_type: str
    required: bool = False
    placeholder: str | None = None
    help_text: str | None = None
    options_json: list[Any] = Field(default_factory=list)
    validation_json: dict[str, Any] = Field(default_factory=dict)
    show_in_table: bool = True
    sort_order: int = 0


class FormFieldCreate(FormFieldBase):
    pass


class FormFieldsSaveRequest(BaseModel):
    fields: list[FormFieldCreate]


class FormFieldOut(FormFieldBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activity_id: int
    created_at: datetime
    updated_at: datetime

