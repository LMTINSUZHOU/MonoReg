from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.types import JSONBType


class Registration(Base):
    __tablename__ = "registrations"
    __table_args__ = (
        UniqueConstraint("activity_id", "email", name="uq_registrations_activity_email"),
        Index("idx_registrations_activity_id", "activity_id"),
        Index("idx_registrations_email", "email"),
        Index("idx_registrations_status", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    phone = Column(String(64), nullable=True)
    status = Column(String(64), nullable=False, default="pending")
    form_data = Column(JSONBType, nullable=False, default=dict)
    submitted_ip = Column(String(64), nullable=True)
    user_agent = Column(Text, nullable=True)
    submitted_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    activity = relationship("Activity", back_populates="registrations")
    account = relationship("Account", back_populates="registration", uselist=False, cascade="all, delete-orphan")
    email_logs = relationship("EmailLog", back_populates="registration")

