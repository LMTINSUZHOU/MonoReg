import smtplib
import time
from datetime import UTC, datetime
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Any

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm.exc import ObjectDeletedError, StaleDataError
from sqlalchemy.orm import Session, joinedload

from app.models import Account, Activity, AdminUser, EmailJob, EmailLog, EmailTemplate, Registration
from app.services.account_service import mark_account_sent
from app.services.settings_service import get_effective_smtp_config
from app.services.template_service import render_for_registration


def get_template_or_404(db: Session, template_id: int) -> EmailTemplate:
    template = db.get(EmailTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="邮件模板不存在")
    return template


def assert_template_activity(template: EmailTemplate, activity_id: int) -> None:
    if template.activity_id != activity_id:
        raise HTTPException(status_code=400, detail="邮件模板不属于当前活动")


def preview_template(
    db: Session,
    *,
    template_id: int,
    registration_id: int | None,
) -> dict[str, Any]:
    template = get_template_or_404(db, template_id)
    activity = db.get(Activity, template.activity_id) if template.activity_id else None
    registration = None
    if registration_id:
        registration = db.execute(
            select(Registration)
            .where(Registration.id == registration_id)
            .options(joinedload(Registration.account), joinedload(Registration.activity))
        ).unique().scalar_one_or_none()
        if not registration:
            raise HTTPException(status_code=404, detail="报名记录不存在")
        assert_template_activity(template, registration.activity_id)
        activity = registration.activity
    if not activity:
        raise HTTPException(status_code=400, detail="需要关联活动或选择报名记录")

    subject, body, missing = render_for_registration(
        db,
        activity,
        registration,
        template.subject,
        template.body,
        include_password=False,
        redact_password=True,
    )
    return {"subject": subject, "body": body, "missing_variables": missing}


def send_smtp(db: Session, to_email: str, subject: str, body: str) -> None:
    smtp_config = get_effective_smtp_config(db)
    if not smtp_config["host"]:
        raise RuntimeError("SMTP 主机未配置")
    if not smtp_config["from_email"]:
        raise RuntimeError("发件邮箱未配置")

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = formataddr((smtp_config["from_name"], smtp_config["from_email"]))
    message["To"] = to_email

    if smtp_config["use_ssl"]:
        client = smtplib.SMTP_SSL(smtp_config["host"], smtp_config["port"], timeout=smtp_config["timeout_seconds"])
    else:
        client = smtplib.SMTP(smtp_config["host"], smtp_config["port"], timeout=smtp_config["timeout_seconds"])

    with client:
        if not smtp_config["use_ssl"]:
            client.starttls()
        if smtp_config["username"]:
            client.login(smtp_config["username"], smtp_config["password"])
        client.sendmail(smtp_config["from_email"], [to_email], message.as_string())


def send_test_email(
    db: Session,
    *,
    template_id: int,
    to_email: str,
    registration_id: int | None,
) -> dict[str, Any]:
    rendered = preview_template(db, template_id=template_id, registration_id=registration_id)
    send_smtp(db, to_email, rendered["subject"], rendered["body"])
    return {"to_email": to_email, "subject": rendered["subject"], "missing_variables": rendered["missing_variables"]}


def create_email_job(
    db: Session,
    *,
    activity_id: int,
    template_id: int,
    registration_ids: list[int],
    skip_sent: bool = True,
    user: AdminUser | None = None,
) -> EmailJob:
    activity = db.get(Activity, activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="活动不存在")
    template = get_template_or_404(db, template_id)
    assert_template_activity(template, activity_id)

    registrations = db.execute(
        select(Registration)
        .where(Registration.activity_id == activity_id, Registration.id.in_(registration_ids))
        .options(joinedload(Registration.account))
        .order_by(Registration.id)
    ).unique().scalars().all()
    if not registrations:
        raise HTTPException(status_code=400, detail="未找到可发送的报名记录")

    job = EmailJob(
        activity_id=activity_id,
        template_id=template_id,
        job_type=template.type,
        status="pending",
        total_count=len(registrations),
        created_by=user.id if user else None,
    )
    db.add(job)
    db.flush()

    for registration in registrations:
        log_status = "pending"
        error_message = None
        account = registration.account
        if template.type == "account_info" and not account:
            log_status = "failed"
            error_message = "账号邮件缺少账号信息"
        if template.type == "account_info" and account and account.sent_at and skip_sent:
            log_status = "skipped"
            error_message = "账号邮件已发送，已跳过"

        subject, body, missing = render_for_registration(
            db,
            activity,
            registration,
            template.subject,
            template.body,
            include_password=False,
            redact_password=True,
        )
        if "账号" in missing or "密码" in missing:
            log_status = "failed"
            error_message = "关键变量缺失: " + ", ".join(missing)

        db.add(
            EmailLog(
                job_id=job.id,
                activity_id=activity_id,
                registration_id=registration.id,
                to_email=registration.email,
                subject=subject,
                body_snapshot=body,
                status=log_status,
                error_message=error_message,
            )
        )

    db.flush()
    update_job_counts(db, job.id)
    return job


def enqueue_email_job(job_id: int) -> bool:
    try:
        from app.workers.queue import get_queue

        queue = get_queue()
        queue.enqueue("app.workers.email_worker.process_email_job", job_id)
        return True
    except Exception:
        return False


def update_job_counts(db: Session, job_id: int) -> None:
    job = db.get(EmailJob, job_id)
    if not job:
        return
    logs = db.execute(select(EmailLog).where(EmailLog.job_id == job_id)).scalars().all()
    job.total_count = len(logs)
    job.success_count = len([item for item in logs if item.status == "sent"])
    job.failed_count = len([item for item in logs if item.status == "failed"])
    if logs and all(item.status in {"sent", "skipped", "failed"} for item in logs):
        job.status = "failed" if job.failed_count and not job.success_count else "completed"
        job.finished_at = datetime.now(UTC).replace(tzinfo=None)


def _safe_commit(db: Session) -> bool:
    try:
        db.commit()
        return True
    except (ObjectDeletedError, StaleDataError):
        db.rollback()
        return False


def _fail_job(db: Session, job_id: int, message: str) -> None:
    job = db.get(EmailJob, job_id)
    if not job:
        return
    job.status = "failed"
    job.finished_at = datetime.now(UTC).replace(tzinfo=None)
    logs = db.execute(
        select(EmailLog).where(EmailLog.job_id == job_id, EmailLog.status.in_(["pending", "retrying"]))
    ).scalars()
    for log in logs:
        log.status = "failed"
        log.error_message = message
    _safe_commit(db)


def process_job_logs(db: Session, job_id: int, *, max_retries: int = 3, rate_limit_seconds: float = 0.25) -> None:
    try:
        job = db.get(EmailJob, job_id)
        if not job:
            return
        activity_id = job.activity_id
        template_id = job.template_id
        template = db.get(EmailTemplate, template_id) if template_id else None
        if not template:
            _fail_job(db, job_id, "邮件模板不存在")
            return
        template_activity_id = template.activity_id
        template_type = template.type
        template_subject = template.subject
        template_body = template.body
        if template_activity_id != activity_id:
            _fail_job(db, job_id, "邮件模板不属于当前活动")
            return
        if not db.get(Activity, activity_id):
            _fail_job(db, job_id, "活动不存在")
            return

        job.status = "running"
        job.started_at = job.started_at or datetime.now(UTC).replace(tzinfo=None)
        if not _safe_commit(db):
            return

        log_ids = db.execute(
            select(EmailLog.id)
            .where(EmailLog.job_id == job_id, EmailLog.status.in_(["pending", "retrying"]))
            .order_by(EmailLog.id)
        ).scalars().all()

        for log_id in log_ids:
            log = db.get(EmailLog, log_id)
            if not log:
                continue
            activity = db.get(Activity, activity_id)
            registration = db.execute(
                select(Registration)
                .where(Registration.id == log.registration_id)
                .options(joinedload(Registration.account))
            ).unique().scalar_one_or_none()
            if not activity or not registration:
                log.status = "failed"
                log.error_message = "活动或报名记录不存在"
                if not _safe_commit(db):
                    return
                continue

            try:
                account = registration.account
                if template_type == "account_info" and not account:
                    raise RuntimeError("账号邮件缺少账号信息")
                subject, body, missing = render_for_registration(
                    db,
                    activity,
                    registration,
                    template_subject,
                    template_body,
                    include_password=True,
                    redact_password=False,
                )
                if template_type == "account_info" and ("账号" in missing or "密码" in missing):
                    raise RuntimeError("账号邮件关键变量缺失")
                log.status = "sending"
                log.subject = subject
                log.body_snapshot = body.replace(rendered_password(account), "******") if account else body
                if not _safe_commit(db):
                    return

                send_smtp(db, log.to_email, subject, body)
                log = db.get(EmailLog, log_id)
                if not log:
                    return
                registration = db.execute(
                    select(Registration)
                    .where(Registration.id == log.registration_id)
                    .options(joinedload(Registration.account))
                ).unique().scalar_one_or_none()
                account = registration.account if registration else None
                log.status = "sent"
                log.error_message = None
                log.sent_at = datetime.now(UTC).replace(tzinfo=None)
                if template_type == "account_info" and account and registration:
                    mark_account_sent(account, registration)
                if not _safe_commit(db):
                    return
                time.sleep(rate_limit_seconds)
            except (ObjectDeletedError, StaleDataError):
                db.rollback()
                return
            except Exception as exc:
                db.rollback()
                log = db.get(EmailLog, log_id)
                if not log:
                    return
                log.retry_count += 1
                log.status = "retrying" if log.retry_count < max_retries else "failed"
                log.error_message = str(exc)[:1000]
                if not _safe_commit(db):
                    return

        update_job_counts(db, job_id)
        _safe_commit(db)
    except (ObjectDeletedError, StaleDataError):
        db.rollback()


def rendered_password(account: Account | None) -> str:
    if not account:
        return ""
    from app.core.encryption import decrypt_text

    return decrypt_text(account.password_encrypted)


def retry_failed_job(db: Session, job_id: int) -> EmailJob:
    job = db.get(EmailJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="邮件任务不存在")
    failed_logs = db.execute(
        select(EmailLog).where(EmailLog.job_id == job_id, EmailLog.status == "failed")
    ).scalars().all()
    for log in failed_logs:
        log.status = "retrying"
        log.error_message = None
    job.status = "pending"
    job.finished_at = None
    db.flush()
    return job
