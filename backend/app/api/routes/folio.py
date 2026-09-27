from decimal import Decimal
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.services.folio_service import add_charge, get_folio, checkout

router = APIRouter(tags=["folio"])


class ChargeIn(BaseModel):
    booking_id: int
    room_number: str
    category: str
    description: str
    amount: Decimal


@router.post("/folio/charge")
def post_charge(payload: ChargeIn, db: Session = Depends(get_db)):
    charge = add_charge(
        db,
        payload.booking_id,
        payload.room_number,
        payload.category,
        payload.description,
        payload.amount,
    )
    return {"folio_id": charge.folio_id}


@router.get("/folio")
def list_charges(booking_id: int, db: Session = Depends(get_db)):
    charges = get_folio(db, booking_id)
    return [
        {
            "folio_id": c.folio_id,
            "category": c.service_category,
            "description": c.item_description,
            "amount": str(c.amount),
            "status": c.payment_status,
        }
        for c in charges
    ]


@router.post("/checkout")
def do_checkout(booking_id: int, db: Session = Depends(get_db)):
    return checkout(db, booking_id)
