"""Phase 9C tests — intent extraction, availability-verified ranking, and
hallucination guards (the LLM must never invent availability)."""

from app.models.amenity import Amenity
from app.services.recommendation_service import (
    recommend_alternatives,
    index_all_amenities,
)
from app.ai.intent_extraction import extract_intent


def _seed_amenities(db):
    spa = Amenity(
        name="Spa",
        category="SPA",
        status="UNAVAILABLE",
        capacity=2,
        description="massage and therapy",
    )
    sauna = Amenity(
        name="Sauna",
        category="SAUNA",
        status="FREE",
        capacity=4,
        description="steam sauna relax",
    )
    pool = Amenity(
        name="Main Pool",
        category="POOL",
        status="FREE",
        capacity=20,
        description="swimming pool",
    )
    gym_occupied = Amenity(
        name="Gym",
        category="GYM",
        status="OCCUPIED",
        capacity=10,
        description="fitness gym",
    )
    db.add_all([spa, sauna, pool, gym_occupied])
    db.commit()
    for a in [spa, sauna, pool, gym_occupied]:
        db.refresh(a)
    index_all_amenities(db)
    return spa, sauna, pool, gym_occupied


def test_intent_extraction_maps_keywords_to_category():
    assert extract_intent("I want a relaxing massage") == "SPA"
    assert extract_intent("Where can I swim") == "POOL"
    assert extract_intent("gibberish xyz") is None


def test_recommendations_only_include_verified_available_amenities(db_session):
    spa, sauna, pool, gym_occupied = _seed_amenities(db_session)

    result = recommend_alternatives(
        db_session,
        guest_id="guest-1",
        query="looking for a spa massage",
        requested_amenity_id=spa.id,
    )

    recommended_ids = {r["amenity_id"] for r in result["recommendations"]}
    assert spa.id not in recommended_ids  # never recommend the unavailable one back
    assert gym_occupied.id not in recommended_ids  # occupied must never appear
    assert result["requested_amenity_available"] is False
    for rec in result["recommendations"]:
        assert rec["availability_verified"] is True


def test_explanation_never_mentions_amenities_outside_verified_list(db_session):
    spa, sauna, pool, gym_occupied = _seed_amenities(db_session)
    result = recommend_alternatives(
        db_session, guest_id="guest-1", query="spa relax", requested_amenity_id=spa.id
    )

    verified_names = {r["name"] for r in result["recommendations"]}
    # "Spa" legitimately appears as the requested (unavailable) amenity being
    # explained — that is not a hallucination. Names of OTHER amenities that
    # never made it into the verified/ranked list (e.g. the occupied Gym) must
    # never leak into the explanation text.
    assert "Gym" not in verified_names
    assert "Gym" not in result["explanation"]


def test_no_recommendations_does_not_fabricate_availability(db_session):
    # All amenities unavailable -> recommendations must be empty, never invented.
    spa = Amenity(
        name="Spa",
        category="SPA",
        status="UNAVAILABLE",
        capacity=2,
        description="massage",
    )
    db_session.add(spa)
    db_session.commit()
    db_session.refresh(spa)
    index_all_amenities(db_session)

    result = recommend_alternatives(
        db_session, guest_id="guest-1", query="spa massage", requested_amenity_id=spa.id
    )
    assert result["recommendations"] == []
    assert (
        "verified alternatives" in result["explanation"].lower()
        or "no verified" in result["explanation"].lower()
    )
