from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user, require_write_user
from app.models import Activity, AdminUser, FormField
from app.schemas.activity import ActivityCreate, ActivityUpdate
from app.schemas.common import ok
from app.services.audit_service import record_audit
from app.services.form_service import list_public_fields
from app.utils.pagination import paginate

router = APIRouter(prefix="/api/admin/activities", tags=["activities"])
public_router = APIRouter(prefix="/api/public/activities", tags=["public"])


def _serialize_activity(activity: Activity) -> dict:
    return {
        "id": activity.id,
        "title": activity.title,
        "slug": activity.slug,
        "description": activity.description,
        "status": activity.status,
        "start_time": activity.start_time,
        "end_time": activity.end_time,
        "max_registrations": activity.max_registrations,
        "need_account": activity.need_account,
        "auto_generate_account": activity.auto_generate_account,
        "send_confirm_email": activity.send_confirm_email,
        "send_account_email_immediately": activity.send_account_email_immediately,
        "login_url": activity.login_url,
        "created_by": activity.created_by,
        "created_at": activity.created_at,
        "updated_at": activity.updated_at,
    }


@router.get("")
def list_activities(
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    status: str | None = None,
    db: Session = Depends(db_session),
    _: AdminUser = Depends(get_current_user),
):
    stmt = select(Activity).order_by(Activity.created_at.desc())
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(or_(Activity.title.ilike(like), Activity.slug.ilike(like)))
    if status:
        stmt = stmt.where(Activity.status == status)
    page_data = paginate(db, stmt, page, page_size)
    page_data["items"] = [_serialize_activity(item) for item in page_data["items"]]
    return ok(page_data)


@router.post("")
def create_activity(
    payload: ActivityCreate,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    activity = Activity(**payload.model_dump(), created_by=user.id)
    db.add(activity)
    try:
        db.flush()
        record_audit(db, user, "activity.create", "activity", activity.id, {"slug": activity.slug}, request.client.host if request.client else None)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="活动 slug 已存在") from exc
    db.refresh(activity)
    return ok(_serialize_activity(activity), "活动已创建")


@router.get("/{activity_id}")
def get_activity(
    activity_id: int,
    db: Session = Depends(db_session),
    _: AdminUser = Depends(get_current_user),
):
    activity = db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    return ok(_serialize_activity(activity))


@router.put("/{activity_id}")
def update_activity(
    activity_id: int,
    payload: ActivityUpdate,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    activity = db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(activity, key, value)
    try:
        record_audit(db, user, "activity.update", "activity", activity.id, {}, request.client.host if request.client else None)
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="活动 slug 已存在") from exc
    db.refresh(activity)
    return ok(_serialize_activity(activity), "活动已更新")


@router.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    activity = db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    db.delete(activity)
    record_audit(db, user, "activity.delete", "activity", activity_id, {}, request.client.host if request.client else None)
    db.commit()
    return ok({"id": activity_id}, "活动已删除")


@router.post("/{activity_id}/publish")
def publish_activity(activity_id: int, db: Session = Depends(db_session), user: AdminUser = Depends(require_write_user)):
    activity = db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    activity.status = "open"
    record_audit(db, user, "activity.publish", "activity", activity_id)
    db.commit()
    return ok(_serialize_activity(activity), "活动已发布")


@router.post("/{activity_id}/close")
def close_activity(activity_id: int, db: Session = Depends(db_session), user: AdminUser = Depends(require_write_user)):
    activity = db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    activity.status = "closed"
    record_audit(db, user, "activity.close", "activity", activity_id)
    db.commit()
    return ok(_serialize_activity(activity), "活动已关闭")


@router.post("/{activity_id}/duplicate")
def duplicate_activity(activity_id: int, db: Session = Depends(db_session), user: AdminUser = Depends(require_write_user)):
    activity = db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    copy = Activity(
        title=f"{activity.title} Copy",
        slug=f"{activity.slug}-copy",
        description=activity.description,
        status="draft",
        start_time=activity.start_time,
        end_time=activity.end_time,
        max_registrations=activity.max_registrations,
        need_account=activity.need_account,
        auto_generate_account=activity.auto_generate_account,
        send_confirm_email=activity.send_confirm_email,
        send_account_email_immediately=activity.send_account_email_immediately,
        login_url=activity.login_url,
        created_by=user.id,
    )
    db.add(copy)
    db.flush()
    for field in activity.form_fields:
        db.add(
            FormField(
                activity_id=copy.id,
                field_key=field.field_key,
                field_label=field.field_label,
                field_type=field.field_type,
                required=field.required,
                placeholder=field.placeholder,
                help_text=field.help_text,
                options_json=field.options_json,
                validation_json=field.validation_json,
                show_in_table=field.show_in_table,
                sort_order=field.sort_order,
            )
        )
    record_audit(db, user, "activity.duplicate", "activity", copy.id, {"source_id": activity.id})
    db.commit()
    db.refresh(copy)
    return ok(_serialize_activity(copy), "活动已复制")


@public_router.get("/{slug}")
def get_public_activity(slug: str, db: Session = Depends(db_session)):
    activity = db.execute(select(Activity).where(Activity.slug == slug)).scalar_one_or_none()
    if not activity or activity.status != "open":
        raise HTTPException(status_code=404, detail="活动不存在")
    fields = list_public_fields(db, activity.id)
    return ok(
        {
            "activity": {
                "id": activity.id,
                "title": activity.title,
                "slug": activity.slug,
                "description": activity.description,
                "status": activity.status,
                "start_time": activity.start_time,
                "end_time": activity.end_time,
                "max_registrations": activity.max_registrations,
                "need_account": activity.need_account,
                "login_url": activity.login_url,
            },
            "fields": [
                {
                    "key": field.field_key,
                    "field_key": field.field_key,
                    "label": field.field_label,
                    "field_label": field.field_label,
                    "type": field.field_type,
                    "field_type": field.field_type,
                    "required": field.required,
                    "placeholder": field.placeholder,
                    "help_text": field.help_text,
                    "options": field.options_json,
                    "options_json": field.options_json,
                    "validation_json": field.validation_json,
                    "show_in_table": field.show_in_table,
                    "sort_order": field.sort_order,
                }
                for field in fields
            ],
        }
    )
