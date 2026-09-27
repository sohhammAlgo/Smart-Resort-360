"""Amenity notification + AI Voice Call escalation (Phase 2/8 feature, preserved).

Push notification -> acknowledged? -> yes: close. no (within ack window): escalate to voice.
Voice is a communication channel only; it must never hold or block the amenity queue —
enforced by keeping this service fully decoupled from amenity_scheduler_service.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.notification import AmenityNotification
from app.kafka.producer import publish
from app.kafka.topics import (
    TOPIC_AMENITY_EVENTS,
    EVENT_NOTIFICATION_SENT,
    EVENT_NOTIFICATION_ACKNOWLEDGED,
    EVENT_NOTIFICATION_ESCALATED,
)
from app.services.voice_call_service import initiate_voice_call

logger = logging.getLogger("notification_service")


def send_push_notification(
    db: Session, waitlist_id: int, guest_id: str
) -> AmenityNotification:
    notif = AmenityNotification(
        waitlist_id=waitlist_id,
        guest_id=guest_id,
        notification_type="PUSH",
        status="SENT",
        sent_at=datetime.now(timezone.utc),
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    publish(
        TOPIC_AMENITY_EVENTS,
        EVENT_NOTIFICATION_SENT,
        {"notification_id": notif.id, "guest_id": guest_id},
    )
    return notif


def acknowledge_notification(db: Session, notification_id: int) -> AmenityNotification:
    notif = db.query(AmenityNotification).get(notification_id)
    if not notif:
        raise ValueError("Notification not found")
    notif.status = "ACKNOWLEDGED"
    notif.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(notif)
    publish(
        TOPIC_AMENITY_EVENTS,
        EVENT_NOTIFICATION_ACKNOWLEDGED,
        {"notification_id": notif.id},
    )
    return notif


def escalate_to_voice_call(db: Session, notification_id: int) -> AmenityNotification:
    """Called by the scheduled escalation check when the ack window has elapsed.

    A voice provider failure is caught and recorded as FAILED — it must never
    corrupt or block waitlist/offer state (see amenity_scheduler_service).
    """
    notif = db.query(AmenityNotification).get(notification_id)
    if not notif or notif.status == "ACKNOWLEDGED":
        return notif
    notif.status = "ESCALATED"
    notif.escalated_at = datetime.now(timezone.utc)
    db.commit()
    publish(
        TOPIC_AMENITY_EVENTS,
        EVENT_NOTIFICATION_ESCALATED,
        {"notification_id": notif.id},
    )
    try:
        initiate_voice_call(guest_id=notif.guest_id, reason="amenity_available")
    except Exception as exc:  # pragma: no cover - provider dependent
        logger.warning(
            "Voice escalation failed for notification %s: %s", notification_id, exc
        )
        notif.status = "FAILED"
        db.commit()
    db.refresh(notif)
    return notif
