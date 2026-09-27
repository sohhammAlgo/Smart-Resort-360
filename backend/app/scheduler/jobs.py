"""APScheduler background jobs:
 - Phase 9A: periodic maintenance-risk evaluation across all active assets.
 - Phase 9B: sweep of expired amenity offers (TIMEOUT -> next-candidate progression).
 - Notification escalation: ack-window sweep -> voice call escalation.
"""

import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.db.session import SessionLocal
from app.services import risk_service, amenity_scheduler_service
from app.services.notification_service import escalate_to_voice_call
from app.models.notification import AmenityNotification

logger = logging.getLogger("scheduler")
_scheduler = BackgroundScheduler()


def run_maintenance_evaluation():
    db = SessionLocal()
    try:
        results = risk_service.evaluate_all_assets(db)
        logger.info("Maintenance evaluation run: %d assets scored", len(results))
    finally:
        db.close()


def run_offer_expiry_sweep():
    db = SessionLocal()
    try:
        count = amenity_scheduler_service.sweep_expired_offers(db)
        if count:
            logger.info("Expired %d amenity offers", count)
    finally:
        db.close()


def run_notification_escalation_sweep():
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(
            seconds=settings.NOTIFICATION_ACK_WINDOW_SECONDS
        )
        pending = (
            db.query(AmenityNotification)
            .filter(
                AmenityNotification.status == "SENT",
                AmenityNotification.sent_at < cutoff,
            )
            .all()
        )
        for notif in pending:
            escalate_to_voice_call(db, notif.id)
    finally:
        db.close()


def start_scheduler():
    if not settings.RUN_SCHEDULER:
        logger.info(
            "RUN_SCHEDULER disabled; background jobs not started (safe for tests/CI)."
        )
        return
    _scheduler.add_job(
        run_maintenance_evaluation,
        "interval",
        minutes=settings.MAINTENANCE_EVAL_INTERVAL_MINUTES,
        id="maintenance_eval",
    )
    _scheduler.add_job(
        run_offer_expiry_sweep, "interval", seconds=15, id="offer_expiry_sweep"
    )
    _scheduler.add_job(
        run_notification_escalation_sweep,
        "interval",
        seconds=15,
        id="notification_escalation",
    )
    _scheduler.start()


def shutdown_scheduler():
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
