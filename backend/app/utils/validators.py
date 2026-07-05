import re
from typing import Any

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_PATTERN = re.compile(r"^[0-9+\-\s()]{6,32}$")
FIELD_KEY_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,127}$")


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.match(value or ""))


def is_valid_phone(value: str | None) -> bool:
    if not value:
        return True
    return bool(PHONE_PATTERN.match(value))


def is_valid_field_key(value: str) -> bool:
    return bool(FIELD_KEY_PATTERN.match(value or ""))


def normalize_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}

