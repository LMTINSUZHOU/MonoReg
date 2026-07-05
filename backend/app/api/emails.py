from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.api.deps import db_session, get_current_user, require_write_user
from app.models import AdminUser, EmailJob, EmailLog, EmailTemplate
from app.schemas.common import ok
from app.schemas.email import EmailTemplateCreate, EmailTemplateUpdate, SendBatchEmailRequest, SendTestEmailRequest, TemplatePreviewRequest
from app.services.audit_service import record_audit
from app.services.email_service import create_email_job, enqueue_email_job, preview_template, retry_failed_job, send_test_email
from app.utils.pagination import paginate

templates_router = APIRouter(prefix="/api/admin/email-templates", tags=["email-templates"])
email_router = APIRouter(prefix="/api/admin/email", tags=["email-jobs"])


def _serialize_template(item: EmailTemplate) -> dict:
    return {
        "id": item.id,
        "activity_id": item.activity_id,
        "name": item.name,
        "type": item.type,
        "subject": item.subject,
        "body": item.body,
        "enabled": item.enabled,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }


def _serialize_job(item: EmailJob, include_logs: bool = False) -> dict:
    data = {
        "id": item.id,
        "activity_id": item.activity_id,
        "template_id": item.template_id,
        "job_type": item.job_type,
        "status": item.status,
        "total_count": item.total_count,
        "success_count": item.success_count,
        "failed_count": item.failed_count,
        "created_by": item.created_by,
        "started_at": item.started_at,
        "finished_at": item.finished_at,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }
    if include_logs:
        data["logs"] = [
            {
                "id": log.id,
                "registration_id": log.registration_id,
                "to_email": log.to_email,
                "subject": log.subject,
                "body_snapshot": log.body_snapshot,
                "status": log.status,
                "error_message": log.error_message,
                "retry_count": log.retry_count,
                "sent_at": log.sent_at,
                "created_at": log.created_at,
            }
            for log in item.logs
        ]
    return data


@templates_router.get("")
def list_templates(
    activity_id: int | None = None,
    type: str | None = None,
    db: Session = Depends(db_session),
    _: AdminUser = Depends(get_current_user),
):
    stmt = select(EmailTemplate).order_by(EmailTemplate.created_at.desc())
    if activity_id:
        stmt = stmt.where(EmailTemplate.activity_id == activity_id)
    if type:
        stmt = stmt.where(EmailTemplate.type == type)
    items = db.execute(stmt).scalars().all()
    return ok([_serialize_template(item) for item in items])


@templates_router.post("")
def create_template(
    payload: EmailTemplateCreate,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    item = EmailTemplate(**payload.model_dump())
    db.add(item)
    db.flush()
    record_audit(db, user, "email_template.create", "email_template", item.id, {}, request.client.host if request.client else None)
    db.commit()
    db.refresh(item)
    return ok(_serialize_template(item), "邮件模板已创建")


@templates_router.put("/{template_id}")
def update_template(
    template_id: int,
    payload: EmailTemplateUpdate,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    item = db.get(EmailTemplate, template_id)
    if not item:
        raise HTTPException(status_code=404, detail="邮件模板不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    record_audit(db, user, "email_template.update", "email_template", item.id, {}, request.client.host if request.client else None)
    db.commit()
    db.refresh(item)
    return ok(_serialize_template(item), "邮件模板已更新")


@templates_router.delete("/{template_id}")
def delete_template(
    template_id: int,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    item = db.get(EmailTemplate, template_id)
    if not item:
        raise HTTPException(status_code=404, detail="邮件模板不存在")
    db.delete(item)
    record_audit(db, user, "email_template.delete", "email_template", template_id, {}, request.client.host if request.client else None)
    db.commit()
    return ok({"id": template_id}, "邮件模板已删除")


@templates_router.post("/{template_id}/preview")
def preview(
    template_id: int,
    payload: TemplatePreviewRequest,
    db: Session = Depends(db_session),
    _: AdminUser = Depends(get_current_user),
):
    return ok(preview_template(db, template_id=template_id, registration_id=payload.registration_id))


@email_router.post("/send-test")
def send_test(
    payload: SendTestEmailRequest,
    db: Session = Depends(db_session),
    _: AdminUser = Depends(require_write_user),
):
    return ok(send_test_email(db, **payload.model_dump()), "测试邮件已发送")


@email_router.post("/send-batch")
def send_batch(
    payload: SendBatchEmailRequest,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    job = create_email_job(db, **payload.model_dump(), user=user)
    record_audit(db, user, "email_job.create", "email_job", job.id, {"total": job.total_count}, request.client.host if request.client else None)
    db.commit()
    enqueued = enqueue_email_job(job.id)
    return ok({"job_id": job.id, "total_count": job.total_count, "enqueued": enqueued}, "邮件任务已创建")


@email_router.get("/jobs")
def list_jobs(
    activity_id: int | None = None,
    status: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(db_session),
    _: AdminUser = Depends(get_current_user),
):
    stmt = select(EmailJob).order_by(EmailJob.created_at.desc())
    if activity_id:
        stmt = stmt.where(EmailJob.activity_id == activity_id)
    if status:
        stmt = stmt.where(EmailJob.status == status)
    page_data = paginate(db, stmt, page, page_size)
    page_data["items"] = [_serialize_job(item) for item in page_data["items"]]
    return ok(page_data)


@email_router.get("/jobs/{job_id}")
def get_job(
    job_id: int,
    db: Session = Depends(db_session),
    _: AdminUser = Depends(get_current_user),
):
    item = db.execute(
        select(EmailJob).where(EmailJob.id == job_id).options(joinedload(EmailJob.logs))
    ).unique().scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="邮件任务不存在")
    return ok(_serialize_job(item, include_logs=True))


@email_router.post("/jobs/{job_id}/retry-failed")
def retry_failed(
    job_id: int,
    request: Request,
    db: Session = Depends(db_session),
    user: AdminUser = Depends(require_write_user),
):
    job = retry_failed_job(db, job_id)
    record_audit(db, user, "email_job.retry_failed", "email_job", job.id, {}, request.client.host if request.client else None)
    db.commit()
    enqueued = enqueue_email_job(job.id)
    return ok({"job_id": job.id, "enqueued": enqueued}, "失败邮件已重新入队")

