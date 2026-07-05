from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("activity_id", "username", name="uq_accounts_activity_username"),
        UniqueConstraint("registration_id", name="uq_accounts_registration_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True)
    registration_id = Column(Integer, ForeignKey("registrations.id", ondelete="CASCADE"), nullable=False, index=True)
    username = Column(String(255), nullable=False)
    password_encrypted = Column(Text, nullable=False)
    status = Column(String(32), nullable=False, default="ready", index=True)
    generated_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    sent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    activity = relationship("Activity", back_populates="accounts")
    registration = relationship("Registration", back_populates="account")
    generator = relationship("AdminUser")

