from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from app.db.session import Base


class GuestFolio(Base):
    __tablename__ = "guest_folio"

    folio_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("bookings.booking_id"))
    room_number = Column(String(10), nullable=False)
    service_category = Column(String(50), nullable=False)
    item_description = Column(String(255), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(String(20), default="PENDING")
