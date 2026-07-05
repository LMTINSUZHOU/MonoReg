from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.types import JSONBType


class FormField(Base):
    __tablename__ = "form_fields"
    __table_args__ = (UniqueConstraint("activity_id", "field_key", name="uq_form_fields_activity_key"),)

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True)
    field_key = Column(String(128), nullable=False)
    field_label = Column(String(255), nullable=False)
    field_type = Column(String(64), nullable=False)
    required = Column(Boolean, nullable=False, default=False)
    placeholder = Column(Text, nullable=True)
    help_text = Column(Text, nullable=True)
    options_json = Column(JSONBType, nullable=False, default=list)
    validation_json = Column(JSONBType, nullable=False, default=dict)
    show_in_table = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    activity = relationship("Activity", back_populates="form_fields")

