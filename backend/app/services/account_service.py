from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.encryption import decrypt_text, encrypt_text
from app.models import Account, Activity, AdminUser, Registration
from app.utils.password import generate_password


def _get_activity(db: Session, activity_id: int) -> Activity:
    activity = db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    return activity


def generate_accounts(
    db: Session,
    *,
    activity_id: int,
    registration_ids: list[int],
    prefix: str,
    start_number: int,
    digits: int,
    password_length: int,
    avoid_ambiguous_chars: bool,
    overwrite: bool,
    user: AdminUser | None,
) -> dict[str, Any]:
    _get_activity(db, activity_id)
    registrations = db.execute(
        select(Registration)
        .where(Registration.activity_id == activity_id, Registration.id.in_(registration_ids))
        .options(joinedload(Registration.account))
        .order_by(Registration.id)
    ).scalars().all()

    found_ids = {item.id for item in registrations}
    errors = [
        {"registration_id": reg_id, "message": "报名记录不存在"}
        for reg_id in registration_ids
        if reg_id not in found_ids
    ]
    created_count = 0
    skipped_count = 0
    current_number = start_number

    for registration in registrations:
        username = f"{prefix}{str(current_number).zfill(max(digits, 1))}"
        current_number += 1
        existing = registration.account
        duplicate = db.execute(
            select(Account).where(Account.activity_id == activity_id, Account.username == username)
        ).scalar_one_or_none()
        if duplicate and (not existing or duplicate.id != existing.id):
            errors.append({"registration_id": registration.id, "message": f"账号已存在: {username}"})
            skipped_count += 1
            continue

        password = generate_password(password_length, avoid_ambiguous_chars)
        encrypted = encrypt_text(password)
        if existing:
            if not overwrite:
                skipped_count += 1
                continue
            existing.username = username
            existing.password_encrypted = encrypted
            existing.status = "ready"
            existing.sent_at = None
        else:
            db.add(
                Account(
                    activity_id=activity_id,
                    registration_id=registration.id,
                    username=username,
                    password_encrypted=encrypted,
                    status="ready",
                    generated_by=user.id if user else None,
                )
            )
        registration.status = "account_ready"
        created_count += 1

    db.flush()
    return {"created_count": created_count, "skipped_count": skipped_count, "errors": errors}


def import_accounts(
    db: Session,
    *,
    activity_id: int,
    rows: list[dict[str, Any]],
    match_field: str = "email",
    overwrite: bool = False,
    user: AdminUser | None = None,
) -> dict[str, Any]:
    _get_activity(db, activity_id)
    imported_count = 0
    errors: list[dict[str, Any]] = []

    for offset, row in enumerate(rows, start=2):
        email = str(row.get("email") or "").strip()
        username = str(row.get("username") or "").strip()
        password = str(row.get("password") or "").strip()
        if not email or not username or not password:
            errors.append({"row": offset, "field": "email/username/password", "message": "缺少必填字段"})
            continue

        registration = db.execute(
            select(Registration).where(Registration.activity_id == activity_id, Registration.email == email)
        ).scalar_one_or_none()
        if not registration:
            errors.append({"row": offset, "field": match_field, "message": "邮箱不存在", "raw_value": email})
            continue

        duplicate = db.execute(
            select(Account).where(Account.activity_id == activity_id, Account.username == username)
        ).scalar_one_or_none()
        existing = db.execute(
            select(Account).where(Account.registration_id == registration.id)
        ).scalar_one_or_none()
        if duplicate and (not existing or duplicate.id != existing.id):
            errors.append({"row": offset, "field": "username", "message": "账号重复", "raw_value": username})
            continue
        if existing and not overwrite:
            errors.append({"row": offset, "field": "email", "message": "该报名用户已有账号", "raw_value": email})
            continue

        encrypted = encrypt_text(password)
        if existing:
            existing.username = username
            existing.password_encrypted = encrypted
            existing.status = "ready"
            existing.sent_at = None
        else:
            db.add(
                Account(
                    activity_id=activity_id,
                    registration_id=registration.id,
                    username=username,
                    password_encrypted=encrypted,
                    status="ready",
                    generated_by=user.id if user else None,
                )
            )
        registration.status = "account_ready"
        imported_count += 1

    return {"imported_count": imported_count, "failed_count": len(errors), "errors": errors}


def reset_passwords(
    db: Session,
    *,
    account_ids: list[int],
    password_length: int,
    avoid_ambiguous_chars: bool = True,
) -> dict[str, Any]:
    accounts = db.execute(select(Account).where(Account.id.in_(account_ids))).scalars().all()
    for account in accounts:
        account.password_encrypted = encrypt_text(generate_password(password_length, avoid_ambiguous_chars))
        account.status = "ready"
        account.sent_at = None
    return {"updated_count": len(accounts)}


def get_account_secret(account: Account | None) -> tuple[str, str]:
    if not account:
        return "", ""
    return account.username, decrypt_text(account.password_encrypted)


def list_accounts_query(activity_id: int | None, keyword: str | None, status: str | None):
    stmt = select(Account).options(joinedload(Account.registration)).order_by(Account.created_at.desc())
    if activity_id:
        stmt = stmt.where(Account.activity_id == activity_id)
    if status:
        stmt = stmt.where(Account.status == status)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.join(Registration).where(
            or_(Account.username.ilike(like), Registration.email.ilike(like), Registration.name.ilike(like))
        )
    return stmt


def mark_account_sent(account: Account, registration: Registration) -> None:
    account.status = "sent"
    account.sent_at = datetime.now(UTC).replace(tzinfo=None)
    registration.status = "account_sent"

