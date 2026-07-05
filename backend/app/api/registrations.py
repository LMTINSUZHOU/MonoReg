from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import db_session, get_current_user, require_write_user
from app.models import AdminUser, Registration
from app.schemas.common import ok
from app.schemas.registration import BatchStatusUpdate, PublicRegistrationCreate, RegistrationUpdate
from app.services.audit_service import record_audit
from app.services.email_service import enqueue_email_job
from app.services.registration_service import create_public_registration, registrations_query
from app.utils.pagination import paginate

admin_router = APIRouter(prefix="/api/admin/registrations", tags=["registrations"])
public_router = APIRouter(prefix="/api/public/activities", tags=["public-registrations"])


def _serialize_registration(item: Registration) -> dict:
    account = item.account
    return {
        "id": item.id,
        "activity_id": item.activity_id,
        "name": item.name,
        "email": item.email,
        "phone": item.phone,
        "status": item.status,
        "form_data": item.form_data,
        "submitted_ip": item.submitted_ip,
        "user_agent": item.user_agent,
        "submitted_at": item.submitted_at,
        "updated_at": item.updated_at,
        "account": {
            "id": account.id,
            "username": account.username,
            "status": account.status,
            "sent_at": account.sent_at,
        }
        if account
        else None,
    }


@public_router.post("/{slug}/register")
def public_register(
    slug: str,
    payload: PublicRegistrationCreate,
    request: Request,
    db: Session = Depends(db_session),
):
    registration, job_ids = create_public_registration(db, slug=slug, payload=payload, request=request)
    db.commit()
    for job_id in job_ids:
        enqueue_email_job(job_id)
    return ok({"registration_id": registration.id, "status": registration.status}, "报名成功")


@admin_router.get("")
def list_registrations(
    activity_id: int | None = None,
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    status: str | None = None,
    has_account: bool | None = None,
    db: Session = Depends(db_session),
    _: AdminUser = Depends(get_current_user),
):
    stmt = registrations_query(activity_id=activity_id, keyword=keyword, status=status, has_account=has_account)
    page_data = paginate(db, stmt, page, page_size)
    page_data["items"] = [_serialize_registration(item) for item in page_data["items"]]
    return ok(page_data)


@admin_router.get("/{registration_id}")
def get_registration(
    registration_id: int,
    db: Session = Depends(db_session),
    _: AdminUser = Depends(get_current_user),
):
    item = db.execute(
        select(Registration)
        .where(Registration.id == registration_id)
        .options(joinedload(Registration.account), joinedload(Registration.activity))
    ).unique().scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="报名记录不存在")
    data = _serialize_registration(item)
    data["activity"] = {"id": item.activity.id, "title": item.activity.title, "slug": item.activity.slug}
    return ok(data)


@admin_router.put("/{registration_id}")
def update_registration(
    registration_id: int,
    payload: RegistrationUpdate,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    item = db.get(Registration, registration_id)
    if not item:
        raise HTTPException(status_code=404, detail="报名记录不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    record_audit(db, user, "registration.update", "registration", item.id, {}, request.client.host if request.client else None)
    db.commit()
    db.refresh(item)
    return ok(_serialize_registration(item), "报名记录已更新")


@admin_router.post("/batch-update-status")
def batch_update_status(
    payload: BatchStatusUpdate,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    items = db.execute(select(Registration).where(Registration.id.in_(payload.registration_ids))).scalars().all()
    for item in items:
        item.status = payload.status
    record_audit(
        db,
        user,
        "registration.batch_update_status",
        "registration",
        None,
        {"ids": payload.registration_ids, "status": payload.status},
        request.client.host if request.client else None,
    )
    db.commit()
    return ok({"updated_count": len(items)}, "状态已更新")


@admin_router.delete("/{registration_id}")
def delete_registration(
    registration_id: int,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    item = db.get(Registration, registration_id)
    if not item:
        raise HTTPException(status_code=404, detail="报名记录不存在")
    db.delete(item)
    record_audit(db, user, "registration.delete", "registration", registration_id, {}, request.client.host if request.client else None)
    db.commit()
    return ok({"id": registration_id}, "报名记录已删除")

