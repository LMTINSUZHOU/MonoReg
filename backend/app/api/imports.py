from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import db_session, require_write_user
from app.models import Activity, AdminUser, Registration
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
    activity = db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    rows = await read_upload_rows(file)
    imported = 0
    errors: list[dict] = []
    seen_emails: set[str] = set()
    for offset, row in enumerate(rows, start=2):
        email = str(row.get("email") or row.get("邮箱") or "").strip()
        if not email:
            errors.append({"row": offset, "field": "email", "message": "缺少邮箱"})
            continue
        normalized_email = email.lower()
        if normalized_email in seen_emails:
            errors.append({"row": offset, "field": "email", "message": "导入文件内邮箱重复", "raw_value": email})
            continue
        seen_emails.add(normalized_email)
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
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="导入数据存在重复或关联冲突，请检查邮箱和活动") from exc
    return ok(result, "报名数据导入完成")
