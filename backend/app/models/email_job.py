from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmailJob(Base):
    __tablename__ = "email_jobs"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(Integer, ForeignKey("email_templates.id"), nullable=True)
    job_type = Column(String(64), nullable=False)
    status = Column(String(32), nullable=False, default="pending", index=True)
    total_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failed_count = Column(Integer, nullable=False, default=0)
    created_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    activity = relationship("Activity", back_populates="email_jobs")
    template = relationship("EmailTemplate", back_populates="jobs")
    creator = relationship("AdminUser")
    logs = relationship("EmailLog", back_populates="job", cascade="all, delete-orphan")

