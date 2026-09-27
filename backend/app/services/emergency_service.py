"""SOS + manager emergency broadcast (F13)."""

from sqlalchemy.orm import Session

from app.models.emergency import EmergencyAlert
from app.kafka.producer import publish
from app.kafka.topics import (
    TOPIC_EMERGENCY_EVENTS,
    EVENT_SOS_CREATED,
    EVENT_EMERGENCY_BROADCAST,
)

FIRST_RESPONDER_DEPARTMENT_BY_TYPE = {
    "MEDICAL": "MEDICAL",
    "FIRE": "SAFETY",
    "SECURITY": "SECURITY",
}


def create_sos(
    db: Session, initiator_role: str, location: str, alert_type: str, message: str
) -> EmergencyAlert:
    alert = EmergencyAlert(
        initiator_role=initiator_role,
        location=location,
        alert_type=alert_type,
        message=message,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    responder_dept = FIRST_RESPONDER_DEPARTMENT_BY_TYPE.get(
        alert_type.upper(), "SAFETY"
    )
    publish(
        TOPIC_EMERGENCY_EVENTS,
        EVENT_SOS_CREATED,
        {
            "alert_id": alert.alert_id,
            "location": location,
            "alert_type": alert_type,
            "routed_to_department": responder_dept,
        },
    )
    return alert


def broadcast_emergency(
    db: Session, manager_id: str, message: str, location: str = "PROPERTY_WIDE"
) -> EmergencyAlert:
    alert = EmergencyAlert(
        initiator_role="MANAGER",
        location=location,
        alert_type="EVACUATION",
        message=message,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    publish(
        TOPIC_EMERGENCY_EVENTS,
        EVENT_EMERGENCY_BROADCAST,
        {"alert_id": alert.alert_id, "issued_by": manager_id},
    )
    return alert
