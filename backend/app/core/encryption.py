import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import settings


def _fernet_key() -> bytes:
    digest = hashlib.sha256(settings.password_encryption_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_text(value: str) -> str:
    return Fernet(_fernet_key()).encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_text(value: str) -> str:
    return Fernet(_fernet_key()).decrypt(value.encode("utf-8")).decode("utf-8")

