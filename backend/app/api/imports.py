from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import db_session, require_write_user
from app.models import AdminUser, Registration
from app.schemas.common import ok
from app.services.audit_service import record_audit
from app.services.import_service import read_upload_rows

router = APIRouter(prefix="/api/admin/import", tags=["imports"])


@router.post("/registrations")
async def import_registrations(
    request: Request,
    file: UploadFile = File(...),
    activity_id: int = Form(...),
    overwrite: bool = Form(False),
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    rows = await read_upload_rows(file)
    imported = 0
    errors: list[dict] = []
    for offset, row in enumerate(rows, start=2):
        email = str(row.get("email") or row.get("邮箱") or "").strip()
        if not email:
            errors.append({"row": offset, "field": "email", "message": "缺少邮箱"})
            continue
        existing = db.query(Registration).filter(
            Registration.activity_id == activity_id, Registration.email == email
        ).first()
        if existing and not overwrite:
            errors.append({"row": offset, "field": "email", "message": "该邮箱已存在", "raw_value": email})
            continue
        target = existing or Registration(activity_id=activity_id, email=email)
        target.name = str(row.get("name") or row.get("姓名") or target.name or "").strip() or None
        target.phone = str(row.get("phone") or row.get("手机号") or target.phone or "").strip() or None
        target.status = str(row.get("status") or row.get("报名状态") or target.status or "pending").strip()
        target.form_data = {
            key: value
            for key, value in row.items()
            if key not in {"email", "邮箱", "name", "姓名", "phone", "手机号", "status", "报名状态"}
        }
        if not existing:
            db.add(target)
        imported += 1
    result = {"imported_count": imported, "failed_count": len(errors), "errors": errors}
    record_audit(db, user, "registration.import", "activity", activity_id, result, request.client.host if request.client else None)
    db.commit()
    return ok(result, "报名数据导入完成")

