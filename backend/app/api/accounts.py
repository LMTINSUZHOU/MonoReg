from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user, require_write_user
from app.models import AdminUser
from app.schemas.account import AccountGenerateRequest, AccountResetPasswordRequest
from app.schemas.common import ok
from app.services.account_service import generate_accounts, import_accounts, list_accounts_query, reset_passwords
from app.services.audit_service import record_audit
from app.services.import_service import read_upload_rows
from app.utils.pagination import paginate
from app.utils.validators import normalize_bool

router = APIRouter(prefix="/api/admin/accounts", tags=["accounts"])


def _serialize_account(account) -> dict:
    registration = account.registration
    return {
        "id": account.id,
        "activity_id": account.activity_id,
        "registration_id": account.registration_id,
        "username": account.username,
        "status": account.status,
        "generated_by": account.generated_by,
        "sent_at": account.sent_at,
        "created_at": account.created_at,
        "updated_at": account.updated_at,
        "registration": {
            "id": registration.id,
            "name": registration.name,
            "email": registration.email,
            "phone": registration.phone,
            "status": registration.status,
        }
        if registration
        else None,
    }


@router.get("")
def list_accounts(
    activity_id: int | None = None,
    keyword: str | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(db_session),
    _: AdminUser = Depends(get_current_user),
):
    page_data = paginate(db, list_accounts_query(activity_id, keyword, status), page, page_size)
    page_data["items"] = [_serialize_account(item) for item in page_data["items"]]
    return ok(page_data)


@router.post("/generate")
def generate(
    payload: AccountGenerateRequest,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    result = generate_accounts(db, **payload.model_dump(), user=user)
    record_audit(db, user, "account.generate", "activity", payload.activity_id, result, request.client.host if request.client else None)
    db.commit()
    return ok(result, "账号生成完成")


@router.post("/import")
async def import_file(
    request: Request,
    file: UploadFile = File(...),
    activity_id: int = Form(...),
    match_field: str = Form("email"),
    overwrite: str = Form("false"),
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    rows = await read_upload_rows(file)
    result = import_accounts(
        db,
        activity_id=activity_id,
        rows=rows,
        match_field=match_field,
        overwrite=normalize_bool(overwrite),
        user=user,
    )
    record_audit(db, user, "account.import", "activity", activity_id, result, request.client.host if request and request.client else None)
    db.commit()
    return ok(result, "账号导入完成")


@router.post("/reset-password")
def reset_password(
    payload: AccountResetPasswordRequest,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    result = reset_passwords(db, **payload.model_dump())
    record_audit(db, user, "account.reset_password", "account", None, {"ids": payload.account_ids}, request.client.host if request.client else None)
    db.commit()
    return ok(result, "密码已重置")
