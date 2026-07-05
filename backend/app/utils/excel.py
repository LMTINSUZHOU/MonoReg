import csv
from io import BytesIO, StringIO
from typing import Any

from openpyxl import Workbook, load_workbook


def read_csv_bytes(content: bytes) -> list[dict[str, str]]:
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(StringIO(text))
    return [dict(row) for row in reader]


def read_xlsx_bytes(content: bytes) -> list[dict[str, Any]]:
    workbook = load_workbook(BytesIO(content), read_only=True, data_only=True)
    sheet = workbook.active
    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(cell).strip() if cell is not None else "" for cell in rows[0]]
    result: list[dict[str, Any]] = []
    for row in rows[1:]:
        result.append({headers[idx]: value for idx, value in enumerate(row) if idx < len(headers)})
    return result


def workbook_to_bytes(headers: list[str], rows: list[list[Any]]) -> bytes:
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    output = BytesIO()
    workbook.save(output)
    return output.getvalue()

