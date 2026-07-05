from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmailLog(Base):
    __tablename__ = "email_logs"
    __table_args__ = (
        Index("idx_email_logs_job_id", "job_id"),
        Index("idx_email_logs_status", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("email_jobs.id", ondelete="CASCADE"), nullable=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True)
    registration_id = Column(Integer, ForeignKey("registrations.id", ondelete="SET NULL"), nullable=True, index=True)
    to_email = Column(String(255), nullable=False)
    subject = Column(Text, nullable=False)
    body_snapshot = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    job = relationship("EmailJob", back_populates="logs")
    registration = relationship("Registration", back_populates="email_logs")

