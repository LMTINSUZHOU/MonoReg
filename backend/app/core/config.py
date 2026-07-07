from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "MonoReg"
    app_env: str = "development"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 1440

    database_url: str = "postgresql+psycopg2://monoreg:monoreg@localhost:5432/monoreg"
    redis_url: str = "redis://localhost:6379/0"

    password_encryption_key: str = "change-me-32-byte-key"

    smtp_host: str = "smtp.example.com"
    smtp_port: int = 465
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_name: str = "MonoReg"
    smtp_from_email: str = "noreply@example.com"
    smtp_use_ssl: bool = True
    smtp_timeout_seconds: int = 20

    backend_cors_origins: str = "http://localhost:5173"
    max_upload_size_mb: int = 10
    max_import_rows: int = 5000
    public_rate_limit_per_minute: int = 30

    init_admin_username: str = "admin"
    init_admin_email: str = "admin@example.com"
    init_admin_password: str = "admin123456"

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.backend_cors_origins.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
