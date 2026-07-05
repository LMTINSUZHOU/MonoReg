from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models import Activity, FormField
from app.schemas.form import FormFieldCreate
from app.utils.validators import is_valid_field_key


FIELD_TYPES = {
    "text",
    "textarea",
    "email",
    "phone",
    "number",
    "select",
    "multi_select",
    "radio",
    "checkbox",
    "date",
}

CORE_FIELDS = [
    {
        "field_key": "name",
        "field_label": "姓名",
        "field_type": "text",
        "required": True,
        "placeholder": "请输入姓名",
        "help_text": "",
        "options_json": [],
        "validation_json": {"max_length": 50},
        "show_in_table": True,
        "sort_order": 1,
    },
    {
        "field_key": "email",
        "field_label": "邮箱",
        "field_type": "email",
        "required": True,
        "placeholder": "请输入邮箱",
        "help_text": "",
        "options_json": [],
        "validation_json": {},
        "show_in_table": True,
        "sort_order": 2,
    },
    {
        "field_key": "phone",
        "field_label": "手机号",
        "field_type": "phone",
        "required": False,
        "placeholder": "请输入手机号",
        "help_text": "",
        "options_json": [],
        "validation_json": {},
        "show_in_table": True,
        "sort_order": 3,
    },
]


def get_activity_or_404(db: Session, activity_id: int) -> Activity:
    activity = db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="活动不存在")
    return activity


def list_form_fields(db: Session, activity_id: int) -> list[FormField]:
    get_activity_or_404(db, activity_id)
    fields = db.execute(
        select(FormField).where(FormField.activity_id == activity_id).order_by(FormField.sort_order)
    ).scalars().all()
    return fields


def default_form_fields(activity_id: int) -> list[FormField]:
    return [FormField(activity_id=activity_id, **field) for field in CORE_FIELDS]


def list_public_fields(db: Session, activity_id: int) -> list[FormField]:
    fields = list_form_fields(db, activity_id)
    if fields:
        return fields
    return default_form_fields(activity_id)


def validate_fields(fields: list[FormFieldCreate]) -> None:
    if not fields:
        raise HTTPException(status_code=400, detail="至少需要一个字段")

    keys: set[str] = set()
    for field in fields:
        if field.field_type not in FIELD_TYPES:
            raise HTTPException(status_code=400, detail=f"不支持的字段类型: {field.field_type}")
        if not is_valid_field_key(field.field_key):
            raise HTTPException(status_code=400, detail=f"字段 key 不合法: {field.field_key}")
        if field.field_key in keys:
            raise HTTPException(status_code=400, detail=f"字段 key 重复: {field.field_key}")
        keys.add(field.field_key)

    if "email" not in keys:
        raise HTTPException(status_code=400, detail="表单必须包含 email 字段")


def replace_form_fields(db: Session, activity_id: int, fields: list[FormFieldCreate]) -> list[FormField]:
    get_activity_or_404(db, activity_id)
    validate_fields(fields)
    db.execute(delete(FormField).where(FormField.activity_id == activity_id))
    created: list[FormField] = []
    for index, field in enumerate(fields):
        payload = field.model_dump()
        payload["sort_order"] = payload.get("sort_order") or index + 1
        obj = FormField(activity_id=activity_id, **payload)
        db.add(obj)
        created.append(obj)
    db.flush()
    return created

