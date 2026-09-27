"""Phase 9D — end-to-end cross-feature test:
maintenance HIGH risk -> amenity marked UNAVAILABLE -> scheduler stops new
offers -> waitlist preserved -> verified alternatives recommended.
"""

from datetime import date, timedelta

from app.models.asset import Asset
from app.models.amenity import Amenity
from app.models.maintenance import MaintenanceHistory
from app.services import risk_service, amenity_scheduler_service as scheduler
from app.services.recommendation_service import index_all_amenities
from app.kafka.producer import EVENT_LOG


def test_maintenance_driven_unavailability_stops_offers_and_recommends_alternatives(
    db_session,
):
    spa = Amenity(
        name="Spa",
        category="SPA",
        status="FREE",
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
    db_session.add_all([spa, sauna])
    db_session.commit()
    db_session.refresh(spa)
    db_session.refresh(sauna)
    index_all_amenities(db_session)

    from app.models.employee import Employee

    db_session.add(
        Employee(
            employee_id="ENG01",
            full_name="Eng",
            role="ENGINEERING",
            department="ENGINEERING",
            email="e@x.com",
            auth_hash="x",
        )
    )
    db_session.commit()

    asset = Asset(
        asset_type="AC_UNIT",
        room_or_location="Spa",
        linked_amenity_id=spa.id,
        installation_date=date.today() - timedelta(days=6000),
        last_service_date=date.today() - timedelta(days=400),
        service_interval_days=180,
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)
    db_session.add_all(
        [
            MaintenanceHistory(asset_id=asset.asset_id, severity="HIGH", is_complaint=1)
            for _ in range(3)
        ]
    )
    db_session.commit()

    # A guest is waiting for the Spa before maintenance risk is evaluated.
    scheduler.join_waitlist(db_session, spa.id, "guest-1")

    EVENT_LOG.clear()
    risk_service.evaluate_asset(db_session, asset.asset_id)

    db_session.refresh(spa)
    assert spa.status == "UNAVAILABLE"
    assert spa.unavailable_reason == "MAINTENANCE"

    # New offers must not be created while under maintenance.
    offer = scheduler.create_offer(db_session, spa.id)
    assert offer is None

    # Waitlist consistency: the guest's entry is preserved, not deleted.
    from app.models.waitlist import AmenityWaitlist

    entry = (
        db_session.query(AmenityWaitlist)
        .filter(
            AmenityWaitlist.amenity_id == spa.id, AmenityWaitlist.guest_id == "guest-1"
        )
        .first()
    )
    assert entry is not None
    assert entry.status == "WAITING"

    event_types = [e["event_type"] for e in EVENT_LOG]
    assert "maintenance.risk_detected" in event_types
    assert "maintenance.task_created" in event_types
    assert "amenity.status_changed" in event_types
    assert "amenity.alternative_recommended" in event_types


def test_amenity_restored_after_maintenance_resumes_offers(db_session):
    from app.services.amenity_integration_service import (
        mark_amenity_unavailable_for_maintenance,
        restore_amenity_after_maintenance,
    )

    spa = Amenity(
        name="Spa", category="SPA", status="FREE", capacity=2, description="massage"
    )
    db_session.add(spa)
    db_session.commit()
    db_session.refresh(spa)

    asset = Asset(
        asset_type="AC_UNIT", room_or_location="Spa", linked_amenity_id=spa.id
    )
    db_session.add(asset)
    db_session.commit()
    db_session.refresh(asset)

    scheduler.join_waitlist(db_session, spa.id, "guest-1")
    mark_amenity_unavailable_for_maintenance(db_session, spa.id, asset.asset_id)
    db_session.refresh(spa)
    assert spa.status == "UNAVAILABLE"

    restore_amenity_after_maintenance(db_session, spa.id)
    db_session.refresh(spa)
    assert spa.status == "FREE"
    assert spa.unavailable_reason is None
