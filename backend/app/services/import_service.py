from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.utils.excel import read_csv_bytes, read_xlsx_bytes


async def read_upload_rows(file: UploadFile) -> list[dict]:
    content = await file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="导入文件过大")

    filename = (file.filename or "").lower()
    if filename.endswith(".csv"):
        return read_csv_bytes(content)
    if filename.endswith(".xlsx") or filename.endswith(".xlsm"):
        return read_xlsx_bytes(content)
    raise HTTPException(status_code=400, detail="仅支持 CSV 或 XLSX 文件")

