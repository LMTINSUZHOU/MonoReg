from fastapi import HTTPException, UploadFile

from app.core.config import settings
from app.utils.excel import read_csv_bytes, read_xlsx_bytes

CHUNK_SIZE = 1024 * 1024


async def read_upload_rows(file: UploadFile) -> list[dict]:
    filename = (file.filename or "").lower()
    is_csv = filename.endswith(".csv")
    is_excel = filename.endswith(".xlsx") or filename.endswith(".xlsm")
    if not is_csv and not is_excel:
        raise HTTPException(status_code=400, detail="仅支持 CSV 或 XLSX 文件")

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    content = bytearray()
    while True:
        chunk = await file.read(CHUNK_SIZE)
        if not chunk:
            break
        content.extend(chunk)
        if len(content) > max_bytes:
            raise HTTPException(status_code=413, detail="导入文件过大")

    data = bytes(content)
    if is_csv:
        return read_csv_bytes(data, max_rows=settings.max_import_rows)
    if is_excel:
        return read_xlsx_bytes(data, max_rows=settings.max_import_rows)
    raise HTTPException(status_code=400, detail="仅支持 CSV 或 XLSX 文件")
