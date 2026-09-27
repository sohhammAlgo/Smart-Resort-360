from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.models.buggy import BuggyRequest
from app.services.buggy_service import request_buggy

router = APIRouter(prefix="/buggy", tags=["buggy"])


class BuggyRequestIn(BaseModel):
    guest_id: str
    pickup_location: str
    dropoff_location: str


@router.post("/request")
def create_request(payload: BuggyRequestIn, db: Session = Depends(get_db)):
    req = request_buggy(
        db, payload.guest_id, payload.pickup_location, payload.dropoff_location
    )
    return {
        "request_id": req.request_id,
        "status": req.status,
        "eta_minutes": req.eta_minutes,
    }


@router.get("/{request_id}")
def get_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(BuggyRequest).get(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return {
        "request_id": req.request_id,
        "status": req.status,
        "eta_minutes": req.eta_minutes,
        "assigned_driver_id": req.assigned_driver_id,
    }
