from pydantic import BaseModel
from typing import Optional


class AmenityOut(BaseModel):
    id: int
    name: str
    category: str
    status: str
    capacity: int
    description: str

    class Config:
        from_attributes = True


class WaitlistJoinRequest(BaseModel):
    guest_id: str
    booking_id: Optional[int] = None
    vip_tier: int = 0


class OfferActionResponse(BaseModel):
    offer_id: int
    status: str
    message: str
