from sqlalchemy import Column, DateTime, Integer, String, func

from app.core.database import Base
from app.models.types import JSONBType


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(128), unique=True, nullable=False, index=True)
    value_json = Column(JSONBType, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
