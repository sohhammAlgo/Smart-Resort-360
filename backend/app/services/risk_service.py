"""Phase 9A — transparent, configurable weighted maintenance risk scoring.

Weights (PRD-mandated, configurable via env/settings):
  30% service overdue, 20% asset age, 20% usage/occupancy,
  20% previous failures, 10% complaints.

This is deliberately NOT a black-box model: every sub-score and the exact
weights used are stored alongside the result for auditability. An
XGBoost/LightGBM upgrade path exists (see ai/maintenance_model.py) but is only
activated once enough labeled failure history exists — see AGENT_CONTEXT.md.

Hard constraint: without physical sensors this predicts *inspection need*,
never a confirmed physical failure. All outward-facing text must say
"risk"/"recommended inspection", not "broken"/"failed".
"""

import json
from datetime import date, datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.asset import Asset
from app.models.maintenance import MaintenanceHistory, MaintenanceRisk
from app.models.waitlist import AmenityWaitlist
from app.kafka.producer import publish
from app.kafka.topics import (
    TOPIC_MAINTENANCE_EVENTS,
    EVENT_MAINTENANCE_RISK_DETECTED,
    EVENT_MAINTENANCE_TASK_CREATED,
)
from app.services.ticket_service import create_ticket

RULE_VERSION = "weighted-rule-v1"
MAX_REASONABLE_ASSET_AGE_DAYS = 15 * 365  # normalization ceiling for the age sub-score
FAILURE_COUNT_CAP = 5  # normalization ceiling for previous-failures sub-score
COMPLAINT_COUNT_CAP = 5  # normalization ceiling for complaints sub-score
LOOKBACK_DAYS_FOR_USAGE = 30


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _service_overdue_score(asset: Asset, today: date) -> float:
    if not asset.service_interval_days or asset.service_interval_days <= 0:
        return 0.0
    last = asset.last_service_date or asset.installation_date
    if not last:
        return 0.5  # unknown service history is itself a moderate risk signal
    days_since = (today - last).days
    ratio = days_since / asset.service_interval_days
    # 0 at ratio<=0.5 (recently serviced), 1.0 once ratio>=1.5 (50% past due)
    return _clamp01((ratio - 0.5) / 1.0)


def _asset_age_score(asset: Asset, today: date) -> float:
    if not asset.installation_date:
        return 0.3
    age_days = (today - asset.installation_date).days
    return _clamp01(age_days / MAX_REASONABLE_ASSET_AGE_DAYS)


def _usage_score(db: Session, asset: Asset) -> float:
    """Usage/occupancy proxy: since there is no IoT telemetry, usage is derived
    from application data — the linked amenity's recent waitlist/demand volume."""
    if not asset.linked_amenity_id:
        return 0.2  # neutral-low default for assets with no usage proxy available
    count = (
        db.query(AmenityWaitlist)
        .filter(AmenityWaitlist.amenity_id == asset.linked_amenity_id)
        .count()
    )
    # Heuristic normalization: 20+ waitlist joins historically implies heavy usage.
    return _clamp01(count / 20.0)


def _previous_failures_score(db: Session, asset: Asset) -> float:
    count = (
        db.query(MaintenanceHistory)
        .filter(
            MaintenanceHistory.asset_id == asset.asset_id,
            MaintenanceHistory.severity.in_(["MEDIUM", "HIGH"]),
        )
        .count()
    )
    return _clamp01(count / FAILURE_COUNT_CAP)


def _complaints_score(db: Session, asset: Asset) -> float:
    count = (
        db.query(MaintenanceHistory)
        .filter(
            MaintenanceHistory.asset_id == asset.asset_id,
            MaintenanceHistory.is_complaint == 1,
        )
        .count()
    )
    return _clamp01(count / COMPLAINT_COUNT_CAP)


def compute_risk(db: Session, asset: Asset, today: Optional[date] = None) -> dict:
    today = today or datetime.now(timezone.utc).date()
    weights = {
        "service_overdue": settings.RISK_WEIGHT_SERVICE_OVERDUE,
        "asset_age": settings.RISK_WEIGHT_ASSET_AGE,
        "usage": settings.RISK_WEIGHT_USAGE,
        "previous_failures": settings.RISK_WEIGHT_PREVIOUS_FAILURES,
        "complaints": settings.RISK_WEIGHT_COMPLAINTS,
    }
    scores = {
        "service_overdue": _service_overdue_score(asset, today),
        "asset_age": _asset_age_score(asset, today),
        "usage": _usage_score(db, asset),
        "previous_failures": _previous_failures_score(db, asset),
        "complaints": _complaints_score(db, asset),
    }
    total = sum(scores[k] * weights[k] for k in weights)
    total = round(_clamp01(total), 4)
    if total < settings.RISK_LOW_THRESHOLD:
        level = "LOW"
    elif total < settings.RISK_HIGH_THRESHOLD:
        level = "MEDIUM"
    else:
        level = "HIGH"
    service_due = scores["service_overdue"] >= 1.0
    return {
        "total": total,
        "level": level,
        "scores": scores,
        "weights": weights,
        "service_due": service_due,
    }


def evaluate_asset(db: Session, asset_id: int) -> MaintenanceRisk:
    asset = db.query(Asset).get(asset_id)
    if not asset:
        raise ValueError("Asset not found")
    result = compute_risk(db, asset)
    risk_row = MaintenanceRisk(
        asset_id=asset.asset_id,
        risk_score=result["total"],
        risk_level=result["level"],
        model_or_rule_version=RULE_VERSION,
        score_breakdown_json=json.dumps(
            {"scores": result["scores"], "weights": result["weights"]}
        ),
    )
    db.add(risk_row)
    db.commit()
    db.refresh(risk_row)

    publish(
        TOPIC_MAINTENANCE_EVENTS,
        EVENT_MAINTENANCE_RISK_DETECTED,
        {
            "asset_id": asset.asset_id,
            "risk_score": result["total"],
            "risk_level": result["level"],
        },
    )

    if result["level"] == "HIGH" or result["service_due"]:
        ticket = create_ticket(
            db,
            location=asset.room_or_location,
            issue_category=f"preventive_inspection:{asset.asset_type}",
            department="ENGINEERING",
            urgency="HIGH" if result["level"] == "HIGH" else "MEDIUM",
            source="MAINTENANCE_RISK",
        )
        publish(
            TOPIC_MAINTENANCE_EVENTS,
            EVENT_MAINTENANCE_TASK_CREATED,
            {
                "asset_id": asset.asset_id,
                "ticket_id": ticket.ticket_id,
                "risk_level": result["level"],
            },
        )
        # Phase 9D integration hook: HIGH risk on an amenity-linked asset can make
        # the amenity temporarily unavailable and stop new scheduler offers.
        if asset.linked_amenity_id and result["level"] == "HIGH":
            from app.services.amenity_integration_service import (
                mark_amenity_unavailable_for_maintenance,
            )

            mark_amenity_unavailable_for_maintenance(
                db, asset.linked_amenity_id, asset.asset_id
            )

    return risk_row


def evaluate_all_assets(db: Session) -> list[MaintenanceRisk]:
    assets = db.query(Asset).filter(Asset.status == "ACTIVE").all()
    return [evaluate_asset(db, a.asset_id) for a in assets]
