from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(64), nullable=False, index=True)
    subject = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    activity = relationship("Activity", back_populates="email_templates")
    jobs = relationship("EmailJob", back_populates="template")

