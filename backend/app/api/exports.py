from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import db_session, get_current_user
from app.models import AdminUser
from app.services.export_service import export_registrations

router = APIRouter(prefix="/api/admin/export", tags=["exports"])


@router.get("/registrations")
def export_registration_file(
    activity_id: int,
    format: str = "csv",
    status: str | None = None,
    keyword: str | None = None,
    db: Session = Depends(db_session),
    _: AdminUser = Depends(get_current_user),
):
    if format not in {"csv", "xlsx"}:
        raise HTTPException(status_code=400, detail="format 仅支持 csv 或 xlsx")
    try:
        content, media_type, filename = export_registrations(
            db, activity_id=activity_id, file_format=format, status=status, keyword=keyword
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(
        content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

