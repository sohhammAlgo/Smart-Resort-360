from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime, timezone
from app.db.session import Base


class AmenityNotification(Base):
    __tablename__ = "amenity_notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    waitlist_id = Column(Integer, ForeignKey("amenity_waitlist.id"))
    guest_id = Column(String(50), nullable=False)
    notification_type = Column(String(30), nullable=False)  # PUSH, VOICE
    # PENDING, SENT, ACKNOWLEDGED, ESCALATED, FAILED
    status = Column(String(30), default="PENDING")
    sent_at = Column(DateTime, nullable=True)
    acknowledged_at = Column(DateTime, nullable=True)
    escalated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
