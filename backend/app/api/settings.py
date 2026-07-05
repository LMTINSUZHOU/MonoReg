from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user, require_write_user
from app.models import AdminUser
from app.schemas.common import ok
from app.schemas.settings import SmtpSettingsUpdate, SmtpTestRequest
from app.services.audit_service import record_audit
from app.services.email_service import send_smtp
from app.services.settings_service import save_smtp_settings, serialize_smtp_settings

router = APIRouter(prefix="/api/admin/settings", tags=["settings"])


@router.get("/smtp")
def get_smtp_settings(
    db: Session = Depends(db_session),
    _: AdminUser = Depends(get_current_user),
):
    return ok(serialize_smtp_settings(db))


@router.put("/smtp")
def update_smtp_settings(
    payload: SmtpSettingsUpdate,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    data = save_smtp_settings(db, payload)
    record_audit(db, user, "settings.smtp.update", "system_setting", None, {}, request.client.host if request.client else None)
    db.commit()
    return ok(data, "SMTP 设置已保存")


@router.post("/smtp/test")
def test_smtp_settings(
    payload: SmtpTestRequest,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    send_smtp(db, str(payload.to_email), payload.subject, payload.body)
    record_audit(db, user, "settings.smtp.test", "system_setting", None, {"to": str(payload.to_email)}, request.client.host if request.client else None)
    db.commit()
    return ok({"to_email": str(payload.to_email)}, "测试邮件已发送")
