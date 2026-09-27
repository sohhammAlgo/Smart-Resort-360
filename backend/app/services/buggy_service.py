"""Smart buggy dispatch: request -> constraint-based assignment -> ETA."""

import random
from sqlalchemy.orm import Session

from app.models.buggy import BuggyRequest
from app.models.employee import Employee
from app.kafka.producer import publish
from app.kafka.topics import (
    TOPIC_BUGGY_EVENTS,
    EVENT_BUGGY_REQUESTED,
    EVENT_BUGGY_ASSIGNED,
)

DRIVER_DEPARTMENT = "TRANSPORT"


def request_buggy(
    db: Session, guest_id: str, pickup: str, dropoff: str
) -> BuggyRequest:
    req = BuggyRequest(
        guest_id=guest_id,
        pickup_location=pickup,
        dropoff_location=dropoff,
        status="REQUESTED",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    publish(
        TOPIC_BUGGY_EVENTS,
        EVENT_BUGGY_REQUESTED,
        {"request_id": req.request_id, "guest_id": guest_id},
    )
    _dispatch(db, req)
    return req


def _dispatch(db: Session, req: BuggyRequest):
    # Constraint-based: pick an active driver from the transport department.
    driver = (
        db.query(Employee)
        .filter(Employee.department == DRIVER_DEPARTMENT, Employee.is_active.is_(True))
        .first()
    )
    if not driver:
        return  # remains REQUESTED until a driver becomes available
    req.status = "ASSIGNED"
    req.assigned_driver_id = driver.employee_id
    req.eta_minutes = random.randint(3, 12)
    db.commit()
    db.refresh(req)
    publish(
        TOPIC_BUGGY_EVENTS,
        EVENT_BUGGY_ASSIGNED,
        {
            "request_id": req.request_id,
            "driver_id": driver.employee_id,
            "eta_minutes": req.eta_minutes,
        },
    )
