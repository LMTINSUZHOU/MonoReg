from collections import defaultdict, deque
from time import time
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.accounts import router as accounts_router
from app.api.activities import public_router as public_activities_router
from app.api.activities import router as activities_router
from app.api.auth import router as auth_router
from app.api.emails import email_router, templates_router
from app.api.exports import router as exports_router
from app.api.forms import router as forms_router
from app.api.imports import router as imports_router
from app.api.registrations import admin_router as registrations_router
from app.api.registrations import public_router as public_registrations_router
from app.api.settings import router as settings_router
from app.core.config import settings
from app.schemas.common import fail, ok


app = FastAPI(title=settings.app_name, version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_public_hits: dict[str, deque[float]] = defaultdict(deque)


@app.middleware("http")
async def public_rate_limit(request: Request, call_next):
    if request.url.path.startswith("/api/public/") and request.method in {"POST", "PUT", "PATCH"}:
        client_ip = request.client.host if request.client else "unknown"
        now = time()
        hits = _public_hits[client_ip]
        while hits and now - hits[0] > 60:
            hits.popleft()
        if len(hits) >= settings.public_rate_limit_per_minute:
            return JSONResponse(
                status_code=429,
                content=fail("请求过于频繁，请稍后再试", "RATE_LIMITED"),
            )
        hits.append(now)
    return await call_next(request)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(str(exc.detail), "HTTP_ERROR"),
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=fail("请求参数校验失败", "VALIDATION_ERROR", {"errors": exc.errors()}),
    )


@app.exception_handler(Exception)
async def generic_exception_handler(_: Request, exc: Exception):
    if settings.app_env == "development":
        detail: dict[str, Any] = {"error": repr(exc)}
    else:
        detail = {}
    return JSONResponse(status_code=500, content=fail("服务器内部错误", "INTERNAL_ERROR", detail))


@app.get("/api/health")
def health():
    return ok({"status": "ok", "app": settings.app_name})


app.include_router(auth_router)
app.include_router(activities_router)
app.include_router(public_activities_router)
app.include_router(forms_router)
app.include_router(registrations_router)
app.include_router(public_registrations_router)
app.include_router(accounts_router)
app.include_router(templates_router)
app.include_router(email_router)
app.include_router(exports_router)
app.include_router(imports_router)
app.include_router(settings_router)
