from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session


def paginate(db: Session, stmt: Select, page: int = 1, page_size: int = 20):
    page = max(page, 1)
    page_size = min(max(page_size, 1), 200)
    count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
    total = db.execute(count_stmt).scalar_one()
    items = db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).scalars().all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}

