from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.amenity import Amenity
from app.schemas.amenity import AmenityOut, WaitlistJoinRequest, OfferActionResponse
from app.services import amenity_scheduler_service as scheduler
from app.services.recommendation_service import recommend_alternatives

router = APIRouter(prefix="/amenities", tags=["amenities"])


@router.get("", response_model=list[AmenityOut])
def list_amenities(db: Session = Depends(get_db)):
    return db.query(Amenity).all()


@router.get("/{amenity_id}", response_model=AmenityOut)
def get_amenity(amenity_id: int, db: Session = Depends(get_db)):
    amenity = db.query(Amenity).get(amenity_id)
    if not amenity:
        raise HTTPException(status_code=404, detail="Amenity not found")
    return amenity


@router.post("/{amenity_id}/waitlist")
def join_waitlist(
    amenity_id: int, payload: WaitlistJoinRequest, db: Session = Depends(get_db)
):
    amenity = db.query(Amenity).get(amenity_id)
    if not amenity:
        raise HTTPException(status_code=404, detail="Amenity not found")
    entry = scheduler.join_waitlist(
        db, amenity_id, payload.guest_id, payload.booking_id, payload.vip_tier
    )
    if amenity.status == "FREE":
        scheduler.create_offer(db, amenity_id)
    return {"waitlist_id": entry.id, "status": entry.status}


@router.post(
    "/{amenity_id}/offers/{offer_id}/accept", response_model=OfferActionResponse
)
def accept_offer(amenity_id: int, offer_id: int, db: Session = Depends(get_db)):
    try:
        offer = scheduler.accept_offer(db, offer_id)
    except scheduler.DoubleAllocationError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return OfferActionResponse(
        offer_id=offer.offer_id, status=offer.status, message="Reservation confirmed"
    )


@router.post("/{amenity_id}/offers/{offer_id}/skip", response_model=OfferActionResponse)
def skip_offer(amenity_id: int, offer_id: int, db: Session = Depends(get_db)):
    try:
        offer = scheduler.skip_offer(db, offer_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return OfferActionResponse(
        offer_id=offer.offer_id,
        status=offer.status,
        message="Offer skipped, next guest notified",
    )


@router.get("/{amenity_id}/alternatives")
def get_alternatives(
    amenity_id: int, guest_id: str, query: str = "", db: Session = Depends(get_db)
):
    return recommend_alternatives(
        db,
        guest_id=guest_id,
        query=query or "similar amenity",
        requested_amenity_id=amenity_id,
    )
