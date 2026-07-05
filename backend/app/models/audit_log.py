from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.core.database import Base
from app.models.types import JSONBType


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True, index=True)
    action = Column(String(128), nullable=False)
    resource_type = Column(String(128), nullable=True)
    resource_id = Column(Integer, nullable=True)
    detail_json = Column(JSONBType, nullable=False, default=dict)
    ip = Column(String(64), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

