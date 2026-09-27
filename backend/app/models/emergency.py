from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime, timezone
from app.db.session import Base


class EmergencyAlert(Base):
    __tablename__ = "emergency_alerts"

    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    initiator_role = Column(String(20), nullable=False)
    location = Column(String(100), nullable=False)
    alert_type = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
