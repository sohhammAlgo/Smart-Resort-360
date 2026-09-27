"""Phase 9D — Cross-feature integration between maintenance, the priority
scheduler, and alternative recommendations.

Flow: maintenance marks an amenity unavailable -> new offers stop -> the
waitlist is preserved (guests are not silently dropped) -> affected guests are
offered verified alternative amenities.
"""

import logging

from sqlalchemy.orm import Session

from app.models.amenity import Amenity
from app.models.waitlist import AmenityWaitlist
from app.models.amenity_offer import AmenityOffer
from app.kafka.producer import publish
from app.kafka.topics import TOPIC_AMENITY_EVENTS, EVENT_AMENITY_STATUS_CHANGED

logger = logging.getLogger("amenity_integration_service")


def mark_amenity_unavailable_for_maintenance(
    db: Session, amenity_id: int, asset_id: int
) -> Amenity:
    from app.services.amenity_scheduler_service import expire_offer

    amenity = db.query(Amenity).get(amenity_id)
    if not amenity:
        raise ValueError("Amenity not found")
    previous_status = amenity.status
    amenity.status = "UNAVAILABLE"
    amenity.unavailable_reason = "MAINTENANCE"
    db.commit()
    db.refresh(amenity)

    # Cancel any live offer so the resource is not handed out while under maintenance.
    active_offer = (
        db.query(AmenityOffer)
        .filter(AmenityOffer.amenity_id == amenity_id, AmenityOffer.status == "OFFERED")
        .first()
    )
    if active_offer:
        expire_offer(db, active_offer.offer_id)

    publish(
        TOPIC_AMENITY_EVENTS,
        EVENT_AMENITY_STATUS_CHANGED,
        {
            "amenity_id": amenity_id,
            "previous_status": previous_status,
            "new_status": "UNAVAILABLE",
            "reason": "MAINTENANCE",
            "asset_id": asset_id,
        },
    )

    # Waitlist consistency: entries remain WAITING (not deleted/cancelled) — the
    # scheduler simply will not create new offers while status != FREE.
    waiting_guests = (
        db.query(AmenityWaitlist)
        .filter(
            AmenityWaitlist.amenity_id == amenity_id,
            AmenityWaitlist.status == "WAITING",
        )
        .all()
    )
    for entry in waiting_guests:
        try:
            recommend_alternative_for_guest(db, amenity_id, entry.guest_id)
        except Exception as exc:  # pragma: no cover - recommendation is best-effort
            logger.warning(
                "Alternative recommendation failed for guest %s: %s",
                entry.guest_id,
                exc,
            )

    return amenity


def restore_amenity_after_maintenance(db: Session, amenity_id: int) -> Amenity:
    from app.services.amenity_scheduler_service import create_offer

    amenity = db.query(Amenity).get(amenity_id)
    if not amenity:
        raise ValueError("Amenity not found")
    amenity.status = "FREE"
    amenity.unavailable_reason = None
    db.commit()
    db.refresh(amenity)
    publish(
        TOPIC_AMENITY_EVENTS,
        EVENT_AMENITY_STATUS_CHANGED,
        {
            "amenity_id": amenity_id,
            "previous_status": "UNAVAILABLE",
            "new_status": "FREE",
            "reason": "MAINTENANCE_COMPLETE",
        },
    )
    create_offer(db, amenity_id)
    return amenity


def recommend_alternative_for_guest(
    db: Session, unavailable_amenity_id: int, guest_id: str
) -> dict:
    from app.services.recommendation_service import recommend_alternatives

    amenity = db.query(Amenity).get(unavailable_amenity_id)
    query = f"Looking for something similar to {amenity.name if amenity else 'this amenity'}"
    return recommend_alternatives(
        db, guest_id=guest_id, query=query, requested_amenity_id=unavailable_amenity_id
    )
