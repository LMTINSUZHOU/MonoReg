import csv
from io import StringIO
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Account, Activity, FormField, Registration
from app.utils.excel import workbook_to_bytes


def _registration_rows(
    db: Session,
    *,
    activity_id: int,
    status: str | None = None,
    keyword: str | None = None,
) -> tuple[list[str], list[list[Any]]]:
    activity = db.get(Activity, activity_id)
    if not activity:
        raise ValueError("活动不存在")

    fields = db.execute(
        select(FormField)
        .where(FormField.activity_id == activity_id, FormField.show_in_table.is_(True))
        .order_by(FormField.sort_order)
    ).scalars().all()

    stmt = (
        select(Registration)
        .where(Registration.activity_id == activity_id)
        .options(joinedload(Registration.account))
        .order_by(Registration.submitted_at.desc())
    )
    if status:
        stmt = stmt.where(Registration.status == status)
    if keyword:
        like = f"%{keyword}%"
        stmt = stmt.where(
            or_(Registration.name.ilike(like), Registration.email.ilike(like), Registration.phone.ilike(like))
        )
    registrations = db.execute(stmt).unique().scalars().all()

    headers = ["报名ID", "活动名称", "姓名", "邮箱", "手机号", "报名状态", "账号", "账号状态", "报名时间"]
    dynamic_headers = [field.field_label for field in fields if field.field_key not in {"name", "email", "phone"}]
    headers.extend(dynamic_headers)

    rows: list[list[Any]] = []
    for item in registrations:
        account: Account | None = item.account
        row = [
            item.id,
            activity.title,
            item.name or "",
            item.email,
            item.phone or "",
            item.status,
            account.username if account else "",
            account.status if account else "",
            item.submitted_at.isoformat(sep=" ", timespec="seconds") if item.submitted_at else "",
        ]
        for field in fields:
            if field.field_key not in {"name", "email", "phone"}:
                value = item.form_data.get(field.field_key, "")
                if isinstance(value, list):
                    value = ", ".join(map(str, value))
                row.append(value)
        rows.append(row)
    return headers, rows


def export_registrations(
    db: Session,
    *,
    activity_id: int,
    file_format: str,
    status: str | None = None,
    keyword: str | None = None,
) -> tuple[bytes, str, str]:
    headers, rows = _registration_rows(db, activity_id=activity_id, status=status, keyword=keyword)
    if file_format == "xlsx":
        return (
            workbook_to_bytes(headers, rows),
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "registrations.xlsx",
        )

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    writer.writerows(rows)
    return buffer.getvalue().encode("utf-8-sig"), "text/csv; charset=utf-8", "registrations.csv"

