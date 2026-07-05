from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.encryption import decrypt_text, encrypt_text
from app.models import SystemSetting
from app.schemas.settings import SmtpSettingsUpdate


SMTP_SETTING_KEY = "smtp"


def _default_smtp_config() -> dict[str, Any]:
    return {
        "host": settings.smtp_host,
        "port": settings.smtp_port,
        "username": settings.smtp_username,
        "password": settings.smtp_password,
        "from_name": settings.smtp_from_name,
        "from_email": settings.smtp_from_email,
        "use_ssl": settings.smtp_use_ssl,
        "timeout_seconds": settings.smtp_timeout_seconds,
    }


def _smtp_setting_row(db: Session) -> SystemSetting | None:
    return db.execute(select(SystemSetting).where(SystemSetting.key == SMTP_SETTING_KEY)).scalar_one_or_none()


def _stored_smtp_config(row: SystemSetting | None) -> dict[str, Any]:
    config = _default_smtp_config()
    if not row:
        return config

    value = dict(row.value_json or {})
    for key in ("host", "port", "username", "from_name", "from_email", "use_ssl", "timeout_seconds"):
        if key in value and value[key] is not None:
            config[key] = value[key]

    if "password_encrypted" in value:
        encrypted = value.get("password_encrypted")
        config["password"] = decrypt_text(encrypted) if encrypted else ""

    return config


def get_effective_smtp_config(db: Session | None = None) -> dict[str, Any]:
    row = _smtp_setting_row(db) if db else None
    config = _stored_smtp_config(row)
    config["port"] = int(config["port"])
    config["use_ssl"] = bool(config["use_ssl"])
    config["timeout_seconds"] = int(config["timeout_seconds"])
    return config


def serialize_smtp_settings(db: Session) -> dict[str, Any]:
    row = _smtp_setting_row(db)
    config = _stored_smtp_config(row)
    return {
        "host": config["host"],
        "port": int(config["port"]),
        "username": config["username"],
        "from_name": config["from_name"],
        "from_email": config["from_email"],
        "use_ssl": bool(config["use_ssl"]),
        "timeout_seconds": int(config["timeout_seconds"]),
        "password_configured": bool(config.get("password")),
        "source": "database" if row else "environment",
    }


def save_smtp_settings(db: Session, payload: SmtpSettingsUpdate) -> dict[str, Any]:
    row = _smtp_setting_row(db)
    if not row:
        row = SystemSetting(key=SMTP_SETTING_KEY, value_json={})
        db.add(row)

    previous = dict(row.value_json or {})
    password_encrypted = previous.get("password_encrypted")
    if payload.clear_password:
        password_encrypted = ""
    elif payload.password:
        password_encrypted = encrypt_text(payload.password)

    value_json: dict[str, Any] = {
        "host": payload.host.strip(),
        "port": payload.port,
        "username": payload.username.strip(),
        "from_name": payload.from_name.strip(),
        "from_email": str(payload.from_email),
        "use_ssl": payload.use_ssl,
        "timeout_seconds": payload.timeout_seconds,
    }
    if password_encrypted is not None:
        value_json["password_encrypted"] = password_encrypted

    row.value_json = value_json
    db.flush()
    return serialize_smtp_settings(db)
