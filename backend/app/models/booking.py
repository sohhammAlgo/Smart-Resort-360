from sqlalchemy import Column, Integer, String, Date, DateTime
from app.db.session import Base


class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    guest_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    room_number = Column(String(10), nullable=False)
    check_in_date = Column(Date, nullable=False)
    check_out_date = Column(Date, nullable=False)
    booking_status = Column(String(20), default="ACTIVE")
    current_otp = Column(String(4), nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
