from sqlalchemy import Column, Integer, String
from app.db.session import Base


class Amenity(Base):
    __tablename__ = "amenities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    # FREE, OCCUPIED, UNAVAILABLE (e.g. maintenance-driven)
    status = Column(String(20), default="FREE")
    max_duration_minutes = Column(Integer, default=60)
    # Attributes used by the alternative-recommendation ranking/embedding step.
    description = Column(String(500), default="")
    capacity = Column(Integer, default=1)
    unavailable_reason = Column(String(50), nullable=True)  # e.g. MAINTENANCE
