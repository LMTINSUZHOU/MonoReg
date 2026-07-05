from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    success: bool = True
    data: Any = None
    message: str = "ok"


class PageResponse(BaseModel):
    items: list[Any]
    total: int
    page: int
    page_size: int


def ok(data: Any = None, message: str = "ok") -> dict[str, Any]:
    return {"success": True, "data": data, "message": message}


def fail(
    message: str,
    code: str = "BAD_REQUEST",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {"success": False, "message": message, "code": code, "details": details or {}}

