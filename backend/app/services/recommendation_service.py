"""Phase 9C — Context-Aware Amenity Alternatives (Agent 10 / F07C).

Pipeline (each stage uses the right tool for the job, per the PRD's
engineering rule — no single LLM call is ever the source of truth):

  1. LangGraph intent extraction (app/ai/intent_extraction.py)
  2. ChromaDB/embedding candidate retrieval (app/ai/vector_store.py)
  3. Authoritative live-availability filter against PostgreSQL (source of truth)
  4. Deterministic ranking (similarity + verified availability + capacity)
  5. LLM explanation of the verified structured result only (never invents
     availability, capacity, prices, or reservations)
"""

from sqlalchemy.orm import Session

from app.models.amenity import Amenity
from app.ai.intent_extraction import extract_intent
from app.ai.vector_store import query_similar, upsert_amenity
from app.ai.llm_client import get_llm_client
from app.kafka.producer import publish
from app.kafka.topics import (
    TOPIC_RECOMMENDATION_EVENTS,
    EVENT_AMENITY_ALTERNATIVE_RECOMMENDED,
)

RANK_WEIGHT_SIMILARITY = 0.6
RANK_WEIGHT_AVAILABILITY = 0.3
RANK_WEIGHT_CAPACITY = 0.1


def index_all_amenities(db: Session):
    for amenity in db.query(Amenity).all():
        upsert_amenity(
            amenity.id, amenity.name, amenity.category, amenity.description or ""
        )


def _live_availability(db: Session, amenity_id: int) -> bool:
    """PostgreSQL is queried directly (the authoritative source of state) —
    never inferred or guessed by the LLM."""
    amenity = db.query(Amenity).get(amenity_id)
    return bool(amenity and amenity.status == "FREE")


def recommend_alternatives(
    db: Session, guest_id: str, query: str, requested_amenity_id: int | None = None
) -> dict:
    intent_category = extract_intent(query)

    requested_amenity = (
        db.query(Amenity).get(requested_amenity_id) if requested_amenity_id else None
    )
    requested_available = (
        _live_availability(db, requested_amenity_id) if requested_amenity_id else True
    )

    search_text = query if not intent_category else f"{intent_category} {query}"
    if requested_amenity:
        search_text += f" {requested_amenity.category}"

    candidates = query_similar(
        search_text, top_k=10, exclude_amenity_id=requested_amenity_id
    )

    ranked = []
    for amenity_id, similarity in candidates:
        amenity = db.query(Amenity).get(amenity_id)
        if not amenity:
            continue
        available = _live_availability(
            db, amenity_id
        )  # verified against Postgres, not assumed
        if not available:
            continue  # never recommend something not actually free right now
        capacity_score = min(1.0, (amenity.capacity or 1) / 5.0)
        final_score = (
            RANK_WEIGHT_SIMILARITY * similarity
            + RANK_WEIGHT_AVAILABILITY * 1.0  # already filtered to available-only
            + RANK_WEIGHT_CAPACITY * capacity_score
        )
        ranked.append(
            {
                "amenity_id": amenity.id,
                "name": amenity.name,
                "category": amenity.category,
                "similarity_score": round(similarity, 4),
                "availability_verified": True,
                "final_rank_score": round(final_score, 4),
            }
        )
    ranked.sort(key=lambda x: x["final_rank_score"], reverse=True)

    explanation = get_llm_client().explain(
        requested_amenity=requested_amenity.name if requested_amenity else None,
        requested_available=requested_available,
        verified_candidates=ranked,
    )

    if ranked:
        publish(
            TOPIC_RECOMMENDATION_EVENTS,
            EVENT_AMENITY_ALTERNATIVE_RECOMMENDED,
            {
                "guest_id": guest_id,
                "requested_amenity_id": requested_amenity_id,
                "recommended_amenity_ids": [r["amenity_id"] for r in ranked],
            },
        )

    return {
        "intent_category": intent_category,
        "requested_amenity_available": requested_available,
        "recommendations": ranked,
        "explanation": explanation,
    }
