"""Digital folio + zero-queue checkout."""

from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.folio import GuestFolio
from app.models.booking import Booking
from app.kafka.producer import publish
from app.kafka.topics import (
    TOPIC_FOLIO_EVENTS,
    EVENT_FOLIO_CHARGE_ADDED,
    EVENT_CHECKOUT_COMPLETED,
)


def add_charge(
    db: Session,
    booking_id: int,
    room_number: str,
    category: str,
    description: str,
    amount: Decimal,
) -> GuestFolio:
    charge = GuestFolio(
        booking_id=booking_id,
        room_number=room_number,
        service_category=category,
        item_description=description,
        amount=amount,
        payment_status="PENDING",
    )
    db.add(charge)
    db.commit()
    db.refresh(charge)
    publish(
        TOPIC_FOLIO_EVENTS,
        EVENT_FOLIO_CHARGE_ADDED,
        {"folio_id": charge.folio_id, "booking_id": booking_id, "amount": str(amount)},
    )
    return charge


def get_folio(db: Session, booking_id: int):
    return db.query(GuestFolio).filter(GuestFolio.booking_id == booking_id).all()


def checkout(db: Session, booking_id: int) -> dict:
    charges = get_folio(db, booking_id)
    total = sum((c.amount for c in charges), Decimal("0"))
    for c in charges:
        c.payment_status = "PAID"
    booking = db.query(Booking).get(booking_id)
    if booking:
        booking.booking_status = "CHECKED_OUT"
    db.commit()
    publish(
        TOPIC_FOLIO_EVENTS,
        EVENT_CHECKOUT_COMPLETED,
        {"booking_id": booking_id, "total": str(total)},
    )
    return {
        "booking_id": booking_id,
        "total_settled": str(total),
        "status": "CHECKED_OUT",
    }
