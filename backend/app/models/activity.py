from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(128), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="draft", index=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    max_registrations = Column(Integer, nullable=True)
    need_account = Column(Boolean, nullable=False, default=False)
    auto_generate_account = Column(Boolean, nullable=False, default=False)
    send_confirm_email = Column(Boolean, nullable=False, default=False)
    send_account_email_immediately = Column(Boolean, nullable=False, default=False)
    login_url = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    creator = relationship("AdminUser", back_populates="activities")
    form_fields = relationship("FormField", back_populates="activity", cascade="all, delete-orphan")
    registrations = relationship("Registration", back_populates="activity", cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="activity", cascade="all, delete-orphan")
    email_templates = relationship("EmailTemplate", back_populates="activity", cascade="all, delete-orphan")
    email_jobs = relationship("EmailJob", back_populates="activity", cascade="all, delete-orphan")

