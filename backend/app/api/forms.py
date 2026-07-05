from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user, require_write_user
from app.models import AdminUser
from app.schemas.common import ok
from app.schemas.form import FormFieldsSaveRequest
from app.services.audit_service import record_audit
from app.services.form_service import list_form_fields, replace_form_fields

router = APIRouter(prefix="/api/admin/activities/{activity_id}/form-fields", tags=["forms"])


def _field_out(field) -> dict:
    return {
        "id": field.id,
        "activity_id": field.activity_id,
        "field_key": field.field_key,
        "field_label": field.field_label,
        "field_type": field.field_type,
        "required": field.required,
        "placeholder": field.placeholder,
        "help_text": field.help_text,
        "options_json": field.options_json,
        "validation_json": field.validation_json,
        "show_in_table": field.show_in_table,
        "sort_order": field.sort_order,
        "created_at": field.created_at,
        "updated_at": field.updated_at,
    }


@router.get("")
def get_fields(
    activity_id: int,
    db: Session = Depends(db_session),
    _: AdminUser = Depends(get_current_user),
):
    return ok([_field_out(item) for item in list_form_fields(db, activity_id)])


@router.put("")
def save_fields(
    activity_id: int,
    payload: FormFieldsSaveRequest,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    fields = replace_form_fields(db, activity_id, payload.fields)
    record_audit(
        db,
        user,
        "form_fields.replace",
        "activity",
        activity_id,
        {"count": len(fields)},
        request.client.host if request.client else None,
    )
    db.commit()
    return ok([_field_out(item) for item in fields], "表单字段已保存")

