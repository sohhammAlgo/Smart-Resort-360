from pydantic import BaseModel
from typing import List, Optional


class RecommendationRequest(BaseModel):
    guest_id: str
    query: str
    requested_amenity_id: Optional[int] = None


class RecommendedAmenity(BaseModel):
    amenity_id: int
    name: str
    category: str
    similarity_score: float
    availability_verified: bool
    final_rank_score: float


class RecommendationResponse(BaseModel):
    intent_category: Optional[str]
    requested_amenity_available: bool
    recommendations: List[RecommendedAmenity]
    explanation: str
