"""Phase 9B — Dynamic Amenity Priority Scheduler.

Deterministic (never LLM-driven) scheduling engine:
  Redis Sorted Set active queue -> priority score (waiting-time aging + VIP
  fairness) -> short configurable offer TTL -> ACCEPT / SKIP / TIMEOUT ->
  atomic PostgreSQL reservation, preventing double allocation.

Voice calls (notification_service/voice_call_service) are a fully decoupled,
asynchronous communication channel and are never called from this module in a
way that can block or hold the queue.
"""

import time
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.redis_client import get_redis
from app.models.amenity import Amenity
from app.models.waitlist import AmenityWaitlist
from app.models.amenity_offer import AmenityOffer
from app.kafka.producer import publish
from app.kafka.topics import (
    TOPIC_WAITLIST_EVENTS,
    TOPIC_AMENITY_EVENTS,
    EVENT_WAITLIST_JOINED,
    EVENT_AMENITY_OFFER_CREATED,
    EVENT_AMENITY_OFFER_EXPIRED,
    EVENT_AMENITY_RESERVED,
)


def _queue_key(amenity_id: int) -> str:
    return f"amenity_queue:{amenity_id}"


def _meta_key(waitlist_id: int) -> str:
    return f"amenity_queue_meta:{waitlist_id}"


def _offer_key(amenity_id: int) -> str:
    return f"amenity_active_offer:{amenity_id}"


def _lock_key(amenity_id: int) -> str:
    return f"amenity_offer_lock:{amenity_id}"


class DoubleAllocationError(Exception):
    pass


def join_waitlist(
    db: Session,
    amenity_id: int,
    guest_id: str,
    booking_id: int | None = None,
    vip_tier: int = 0,
) -> AmenityWaitlist:
    entry = AmenityWaitlist(
        amenity_id=amenity_id,
        guest_id=guest_id,
        status="WAITING",
        booking_id=booking_id,
        vip_tier=vip_tier,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    r = get_redis()
    now = time.time()
    r.zadd(
        _queue_key(amenity_id), {str(entry.id): vip_tier * 1000}
    )  # base score component (VIP fairness tie-break)
    r.hset(
        _meta_key(entry.id),
        mapping={"joined_at": now, "vip_tier": vip_tier, "guest_id": guest_id},
    )

    publish(
        TOPIC_WAITLIST_EVENTS,
        EVENT_WAITLIST_JOINED,
        {"waitlist_id": entry.id, "amenity_id": amenity_id, "guest_id": guest_id},
    )
    return entry


def _dynamic_priority_score(
    base_score: float, joined_at: float, vip_tier: int
) -> float:
    """Aging/fairness: waiting time increases priority so no guest starves,
    on top of the VIP base component."""
    waited_minutes = max(0.0, (time.time() - joined_at) / 60.0)
    return base_score + waited_minutes * settings.AMENITY_AGING_RATE_PER_MINUTE


def _select_next_candidate(amenity_id: int) -> int | None:
    r = get_redis()
    members = r.zrange(_queue_key(amenity_id), 0, -1, withscores=True)
    if not members:
        return None
    best_id, best_score = None, None
    for member, base_score in members:
        wid = int(member)
        meta = r.hgetall(_meta_key(wid))
        joined_at = float(meta.get("joined_at", time.time()))
        vip_tier = int(float(meta.get("vip_tier", 0)))
        score = _dynamic_priority_score(base_score, joined_at, vip_tier)
        if best_score is None or score > best_score:
            best_id, best_score = wid, score
    return best_id


def create_offer(db: Session, amenity_id: int) -> AmenityOffer | None:
    """Creates the next offer for a FREE amenity. Uses a short Redis lock so
    concurrent triggers cannot create two simultaneous offers for one amenity."""
    r = get_redis()
    amenity = db.query(Amenity).get(amenity_id)
    if not amenity or amenity.status != "FREE":
        return None

    lock_token = str(uuid.uuid4())
    acquired = r.set(_lock_key(amenity_id), lock_token, nx=True, px=5000)
    if not acquired:
        return None
    try:
        # Re-check inside the lock (another worker may have just created an offer).
        if r.exists(_offer_key(amenity_id)):
            return None
        wid = _select_next_candidate(amenity_id)
        if wid is None:
            return None
        entry = db.query(AmenityWaitlist).get(wid)
        if not entry or entry.status not in ("WAITING",):
            r.zrem(_queue_key(amenity_id), str(wid))
            return None

        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=settings.AMENITY_OFFER_TTL_SECONDS
        )
        offer = AmenityOffer(
            amenity_id=amenity_id,
            waitlist_id=wid,
            guest_id=entry.guest_id,
            status="OFFERED",
            expires_at=expires_at,
        )
        entry.status = "OFFERED"
        db.add(offer)
        db.commit()
        db.refresh(offer)

        r.setex(
            _offer_key(amenity_id),
            settings.AMENITY_OFFER_TTL_SECONDS,
            str(offer.offer_id),
        )
        r.zrem(_queue_key(amenity_id), str(wid))

        publish(
            TOPIC_AMENITY_EVENTS,
            EVENT_AMENITY_OFFER_CREATED,
            {
                "offer_id": offer.offer_id,
                "amenity_id": amenity_id,
                "waitlist_id": wid,
                "guest_id": entry.guest_id,
                "expires_at": expires_at.isoformat(),
            },
        )
        return offer
    finally:
        if r.get(_lock_key(amenity_id)) == lock_token:
            r.delete(_lock_key(amenity_id))


def accept_offer(db: Session, offer_id: int) -> AmenityOffer:
    """Atomic reservation: PostgreSQL is the single source of truth for the
    final allocation decision, so double allocation is impossible even if two
    accepts race — only one can win the conditional UPDATE below."""
    r = get_redis()
    offer = db.query(AmenityOffer).get(offer_id)
    if not offer:
        raise ValueError("Offer not found")
    if offer.status != "OFFERED":
        raise DoubleAllocationError(f"Offer already {offer.status}")
    if offer.expires_at and offer.expires_at.replace(
        tzinfo=timezone.utc
    ) < datetime.now(timezone.utc):
        raise DoubleAllocationError("Offer expired")

    amenity = db.query(Amenity).get(offer.amenity_id)
    # Conditional/atomic transition — the WHERE clause on current state is what
    # makes this safe under concurrent accept attempts.
    updated = (
        db.query(Amenity)
        .filter(Amenity.id == amenity.id, Amenity.status == "FREE")
        .update({"status": "OCCUPIED"})
    )
    if updated == 0:
        raise DoubleAllocationError("Amenity no longer available")

    offer.status = "ACCEPTED"
    offer.responded_at = datetime.now(timezone.utc)
    entry = db.query(AmenityWaitlist).get(offer.waitlist_id)
    if entry:
        entry.status = "RESERVED"
    db.commit()
    db.refresh(offer)

    r.delete(_offer_key(offer.amenity_id))
    publish(
        TOPIC_AMENITY_EVENTS,
        EVENT_AMENITY_RESERVED,
        {
            "offer_id": offer.offer_id,
            "amenity_id": offer.amenity_id,
            "guest_id": offer.guest_id,
        },
    )
    return offer


def skip_offer(db: Session, offer_id: int) -> AmenityOffer:
    offer = db.query(AmenityOffer).get(offer_id)
    if not offer or offer.status != "OFFERED":
        raise ValueError("Offer not active")
    offer.status = "SKIPPED"
    offer.responded_at = datetime.now(timezone.utc)
    entry = db.query(AmenityWaitlist).get(offer.waitlist_id)
    if entry:
        entry.status = "SKIPPED"
    db.commit()
    db.refresh(offer)
    get_redis().delete(_offer_key(offer.amenity_id))
    create_offer(db, offer.amenity_id)  # immediately progress to next eligible guest
    return offer


def expire_offer(db: Session, offer_id: int) -> AmenityOffer:
    offer = db.query(AmenityOffer).get(offer_id)
    if not offer or offer.status != "OFFERED":
        return offer
    offer.status = "TIMED_OUT"
    entry = db.query(AmenityWaitlist).get(offer.waitlist_id)
    if entry:
        entry.status = "TIMED_OUT"
    db.commit()
    db.refresh(offer)
    get_redis().delete(_offer_key(offer.amenity_id))
    publish(
        TOPIC_AMENITY_EVENTS,
        EVENT_AMENITY_OFFER_EXPIRED,
        {"offer_id": offer.offer_id, "amenity_id": offer.amenity_id},
    )
    create_offer(db, offer.amenity_id)  # immediate next-candidate progression
    return offer


def sweep_expired_offers(db: Session) -> int:
    """Scheduled job: find OFFERED rows past expiry and time them out."""
    now = datetime.now(timezone.utc)
    expired = (
        db.query(AmenityOffer)
        .filter(AmenityOffer.status == "OFFERED", AmenityOffer.expires_at < now)
        .all()
    )
    for offer in expired:
        expire_offer(db, offer.offer_id)
    return len(expired)


def release_amenity(db: Session, amenity_id: int) -> AmenityOffer | None:
    """Called on checkout/session-end: amenity becomes FREE again and the
    scheduler immediately offers it to the next eligible waiting guest."""
    amenity = db.query(Amenity).get(amenity_id)
    if amenity and amenity.status != "UNAVAILABLE":
        amenity.status = "FREE"
        db.commit()
    return create_offer(db, amenity_id)
