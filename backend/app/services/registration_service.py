from datetime import datetime
from typing import Any

from fastapi import HTTPException, Request
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.models import Activity, EmailTemplate, Registration
from app.schemas.registration import PublicRegistrationCreate
from app.services.account_service import generate_accounts
from app.services.email_service import create_email_job
from app.services.form_service import list_public_fields
from app.utils.validators import is_valid_email, is_valid_phone


def _activity_by_slug(db: Session, slug: str) -> Activity:
    activity = db.execute(select(Activity).where(Activity.slug == slug)).scalar_one_or_none()
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    return activity


def assert_activity_can_register(db: Session, activity: Activity) -> None:
    now = datetime.now()
    if activity.status != "open":
        raise HTTPException(status_code=400, detail="活动当前不开放报名")
    if activity.start_time and now < activity.start_time:
        raise HTTPException(status_code=400, detail="报名尚未开始")
    if activity.end_time and now > activity.end_time:
        raise HTTPException(status_code=400, detail="报名已截止")
    if activity.max_registrations:
        count = db.execute(
            select(func.count()).select_from(Registration).where(Registration.activity_id == activity.id)
        ).scalar_one()
        if count >= activity.max_registrations:
            raise HTTPException(status_code=400, detail="报名人数已满")


def validate_registration_data(db: Session, activity: Activity, payload: PublicRegistrationCreate) -> dict[str, Any]:
    if not is_valid_email(payload.email):
        raise HTTPException(status_code=400, detail="邮箱格式不正确")
    if not is_valid_phone(payload.phone):
        raise HTTPException(status_code=400, detail="手机号格式不正确")

    fields = list_public_fields(db, activity.id)
    form_data = dict(payload.form_data or {})
    core_values = {"name": payload.name, "email": str(payload.email), "phone": payload.phone}

    for field in fields:
        value = core_values.get(field.field_key, form_data.get(field.field_key))
        if field.required and (value is None or value == "" or value == []):
            raise HTTPException(status_code=400, detail=f"字段必填: {field.field_label}")
        if value in (None, ""):
            continue
        if field.field_type == "email" and not is_valid_email(str(value)):
            raise HTTPException(status_code=400, detail=f"{field.field_label} 格式不正确")
        if field.field_type == "phone" and not is_valid_phone(str(value)):
            raise HTTPException(status_code=400, detail=f"{field.field_label} 格式不正确")
        if field.field_type in {"select", "radio"} and field.options_json:
            allowed = {str(item) for item in field.options_json}
            if str(value) not in allowed:
                raise HTTPException(status_code=400, detail=f"{field.field_label} 选项无效")
        if field.field_type == "multi_select" and field.options_json and isinstance(value, list):
            allowed = {str(item) for item in field.options_json}
            if any(str(item) not in allowed for item in value):
                raise HTTPException(status_code=400, detail=f"{field.field_label} 选项无效")

    duplicate = db.execute(
        select(Registration).where(Registration.activity_id == activity.id, Registration.email == str(payload.email))
    ).scalar_one_or_none()
    if duplicate:
        raise HTTPException(status_code=409, detail="该邮箱已报名")

    return form_data


def create_public_registration(
    db: Session,
    *,
    slug: str,
    payload: PublicRegistrationCreate,
    request: Request,
) -> tuple[Registration, list[int]]:
    activity = _activity_by_slug(db, slug)
    assert_activity_can_register(db, activity)
    form_data = validate_registration_data(db, activity, payload)
    registration = Registration(
        activity_id=activity.id,
        name=payload.name,
        email=str(payload.email),
        phone=payload.phone,
        status="pending",
        form_data=form_data,
        submitted_ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(registration)
    try:
        db.flush()
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="该邮箱已报名") from exc

    job_ids: list[int] = []
    if activity.auto_generate_account:
        generate_accounts(
            db,
            activity_id=activity.id,
            registration_ids=[registration.id],
            prefix=f"{activity.slug}_",
            start_number=registration.id,
            digits=4,
            password_length=12,
            avoid_ambiguous_chars=True,
            overwrite=False,
            user=None,
        )

    if activity.send_confirm_email:
        template = db.execute(
            select(EmailTemplate).where(
                EmailTemplate.activity_id == activity.id,
                EmailTemplate.type == "registration_confirm",
                EmailTemplate.enabled.is_(True),
            )
        ).scalar_one_or_none()
        if template:
            job = create_email_job(
                db,
                activity_id=activity.id,
                template_id=template.id,
                registration_ids=[registration.id],
                skip_sent=False,
                user=None,
            )
            job_ids.append(job.id)

    if activity.send_account_email_immediately:
        template = db.execute(
            select(EmailTemplate).where(
                EmailTemplate.activity_id == activity.id,
                EmailTemplate.type == "account_info",
                EmailTemplate.enabled.is_(True),
            )
        ).scalar_one_or_none()
        if template:
            job = create_email_job(
                db,
                activity_id=activity.id,
                template_id=template.id,
                registration_ids=[registration.id],
                skip_sent=True,
                user=None,
            )
            job_ids.append(job.id)

    return registration, job_ids


def registrations_query(
    *,
    activity_id: int | None = None,
    keyword: str | None = None,
    status: str | None = None,
    has_account: bool | None = None,
):
    stmt = select(Registration).options(joinedload(Registration.account)).order_by(Registration.submitted_at.desc())
    if activity_id:
        stmt = stmt.where(Registration.activity_id == activity_id)
    if status:
        stmt = stmt.where(Registration.status == status)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(
            or_(Registration.name.ilike(like), Registration.email.ilike(like), Registration.phone.ilike(like))
        )
    if has_account is True:
        stmt = stmt.where(Registration.account.has())
    if has_account is False:
        stmt = stmt.where(~Registration.account.has())
    return stmt

