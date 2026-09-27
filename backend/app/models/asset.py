from sqlalchemy import Column, Integer, String, Date, ForeignKey
from app.db.session import Base


class Asset(Base):
    """Phase 9A — asset registry backing preventive/risk-based maintenance."""

    __tablename__ = "assets"

    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_type = Column(String(50), nullable=False)
    room_or_location = Column(String(100), nullable=False)
    installation_date = Column(Date, nullable=True)
    last_service_date = Column(Date, nullable=True)
    service_interval_days = Column(Integer, nullable=True)
    status = Column(String(30), default="ACTIVE")
    # Optional link so maintenance can flip an amenity's status (Phase 9D).
    linked_amenity_id = Column(Integer, ForeignKey("amenities.id"), nullable=True)
