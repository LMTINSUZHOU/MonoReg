from pydantic import BaseModel, EmailStr, Field


class SmtpSettingsUpdate(BaseModel):
    host: str = Field(min_length=1, max_length=255)
    port: int = Field(ge=1, le=65535)
    username: str = ""
    password: str | None = None
    clear_password: bool = False
    from_name: str = Field(default="MonoReg", min_length=1, max_length=255)
    from_email: EmailStr
    use_ssl: bool = True
    timeout_seconds: int = Field(default=20, ge=1, le=120)


class SmtpTestRequest(BaseModel):
    to_email: EmailStr
    subject: str = Field(default="MonoReg SMTP 测试", min_length=1, max_length=255)
    body: str = Field(default="这是一封来自 MonoReg 的 SMTP 测试邮件。", min_length=1, max_length=5000)
