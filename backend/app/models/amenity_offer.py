from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime, timezone
from app.db.session import Base


class AmenityOffer(Base):
    """Phase 9B — persistent audit trail of offers made from the priority scheduler.

    The *active* offer + short TTL lives in Redis at runtime; this table is the
    durable audit/history record and backs the atomic reservation transaction.
    """

    __tablename__ = "amenity_offers"

    offer_id = Column(Integer, primary_key=True, autoincrement=True)
    amenity_id = Column(Integer, ForeignKey("amenities.id"))
    waitlist_id = Column(Integer, ForeignKey("amenity_waitlist.id"))
    guest_id = Column(String(50), nullable=False)
    # OFFERED, ACCEPTED, SKIPPED, TIMED_OUT, RESERVED
    status = Column(String(20), default="OFFERED")
    priority_score = Column(String(50), nullable=True)
    offered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    responded_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
