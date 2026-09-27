from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from app.db.session import Base


class BuggyRequest(Base):
    __tablename__ = "buggy_requests"

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    guest_id = Column(String(50), nullable=False)
    pickup_location = Column(String(100), nullable=False)
    dropoff_location = Column(String(100), nullable=False)
    status = Column(
        String(20), default="REQUESTED"
    )  # REQUESTED, ASSIGNED, EN_ROUTE, COMPLETED, CANCELLED
    assigned_driver_id = Column(String(20), nullable=True)
    eta_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
