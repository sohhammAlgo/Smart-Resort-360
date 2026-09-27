from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime, timezone
from app.db.session import Base


class AmenityWaitlist(Base):
    __tablename__ = "amenity_waitlist"

    id = Column(Integer, primary_key=True, autoincrement=True)
    amenity_id = Column(Integer, ForeignKey("amenities.id"))
    guest_id = Column(String(50), nullable=False)
    # WAITING, OFFERED, ACCEPTED, SKIPPED, TIMED_OUT, RESERVED, CANCELLED
    status = Column(String(20), default="WAITING")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    # priority inputs, kept in Postgres for transparency/audit even though the
    # active queue itself lives in a Redis Sorted Set at runtime.
    vip_tier = Column(Integer, default=0)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"), nullable=True)
