from typing import Any

from sqlalchemy.orm import Session

from app.models import AuditLog, AdminUser


def record_audit(
    db: Session,
    user: AdminUser | None,
    action: str,
    resource_type: str | None = None,
    resource_id: int | None = None,
    detail: dict[str, Any] | None = None,
    ip: str | None = None,
) -> AuditLog:
    log = AuditLog(
        admin_id=user.id if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        detail_json=detail or {},
        ip=ip,
    )
    db.add(log)
    return log

