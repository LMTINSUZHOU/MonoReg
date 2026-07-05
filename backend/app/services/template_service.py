from typing import Any

from sqlalchemy.orm import Session

from app.core.encryption import decrypt_text
from app.models import Account, Activity, Registration


VARIABLES = [
    "活动名称",
    "姓名",
    "邮箱",
    "手机号",
    "报名时间",
    "账号",
    "密码",
    "登录地址",
    "报名状态",
]


def build_template_context(
    activity: Activity,
    registration: Registration | None = None,
    account: Account | None = None,
    *,
    include_password: bool = False,
    redact_password: bool = False,
) -> dict[str, Any]:
    password = ""
    if account:
        if redact_password:
            password = "******"
        elif include_password:
            password = decrypt_text(account.password_encrypted)

    return {
        "活动名称": activity.title,
        "姓名": registration.name if registration else "",
        "邮箱": registration.email if registration else "",
        "手机号": registration.phone if registration else "",
        "报名时间": registration.submitted_at.strftime("%Y-%m-%d %H:%M:%S")
        if registration and registration.submitted_at
        else "",
        "账号": account.username if account else "",
        "密码": password,
        "登录地址": activity.login_url or "",
        "报名状态": registration.status if registration else "",
    }


def render_text(template_text: str, context: dict[str, Any]) -> tuple[str, list[str]]:
    rendered = template_text
    missing: list[str] = []
    for variable in VARIABLES:
        token = "{{" + variable + "}}"
        compact_token = "{{ " + variable + " }}"
        value = str(context.get(variable) or "")
        if token in rendered or compact_token in rendered:
            if not value:
                missing.append(variable)
            rendered = rendered.replace(token, value).replace(compact_token, value)
    return rendered, missing


def render_email(
    subject_template: str,
    body_template: str,
    context: dict[str, Any],
) -> tuple[str, str, list[str]]:
    subject, subject_missing = render_text(subject_template, context)
    body, body_missing = render_text(body_template, context)
    missing = sorted(set(subject_missing + body_missing))
    return subject, body, missing


def render_for_registration(
    db: Session,
    activity: Activity,
    registration: Registration | None,
    subject_template: str,
    body_template: str,
    *,
    include_password: bool = False,
    redact_password: bool = False,
) -> tuple[str, str, list[str]]:
    account = None
    if registration:
        account = registration.account or db.query(Account).filter(Account.registration_id == registration.id).first()
    context = build_template_context(
        activity,
        registration,
        account,
        include_password=include_password,
        redact_password=redact_password,
    )
    return render_email(subject_template, body_template, context)

