"""Phase 9A tests — transparent weighted risk scoring."""

from datetime import date, timedelta

from app.models.asset import Asset
from app.services import risk_service
from app.models.maintenance import MaintenanceHistory, MaintenanceRisk
from app.models.ticket import ServiceTicket


def _make_asset(db, **kwargs):
    defaults = dict(asset_type="AC_UNIT", room_or_location="Room 101")
    defaults.update(kwargs)
    asset = Asset(**defaults)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def test_low_risk_for_new_recently_serviced_asset(db_session):
    asset = _make_asset(
        db_session,
        installation_date=date.today() - timedelta(days=30),
        last_service_date=date.today() - timedelta(days=5),
        service_interval_days=180,
    )
    result = risk_service.compute_risk(db_session, asset)
    assert result["level"] == "LOW"
    assert result["total"] < 0.35


def test_high_risk_for_overdue_old_asset_with_failures(db_session):
    asset = _make_asset(
        db_session,
        installation_date=date.today() - timedelta(days=6000),
        last_service_date=date.today() - timedelta(days=400),
        service_interval_days=180,
    )
    db_session.add_all(
        [
            MaintenanceHistory(
                asset_id=asset.asset_id, severity="HIGH", is_complaint=1
            ),
            MaintenanceHistory(
                asset_id=asset.asset_id, severity="HIGH", is_complaint=1
            ),
            MaintenanceHistory(
                asset_id=asset.asset_id, severity="MEDIUM", is_complaint=1
            ),
        ]
    )
    db_session.commit()
    result = risk_service.compute_risk(db_session, asset)
    assert result["level"] == "HIGH"
    assert result["service_due"] is True


def test_weights_sum_to_one():
    from app.core.config import settings

    total = (
        settings.RISK_WEIGHT_SERVICE_OVERDUE
        + settings.RISK_WEIGHT_ASSET_AGE
        + settings.RISK_WEIGHT_USAGE
        + settings.RISK_WEIGHT_PREVIOUS_FAILURES
        + settings.RISK_WEIGHT_COMPLAINTS
    )
    assert abs(total - 1.0) < 1e-9


def test_evaluate_asset_creates_ticket_and_risk_row_for_high_risk(db_session):
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

    asset = _make_asset(
        db_session,
        installation_date=date.today() - timedelta(days=6000),
        last_service_date=date.today() - timedelta(days=400),
        service_interval_days=180,
    )
    db_session.add_all(
        [
            MaintenanceHistory(asset_id=asset.asset_id, severity="HIGH", is_complaint=1)
            for _ in range(3)
        ]
    )
    db_session.commit()

    risk_service.evaluate_asset(db_session, asset.asset_id)

    assert (
        db_session.query(MaintenanceRisk)
        .filter(MaintenanceRisk.asset_id == asset.asset_id)
        .count()
        == 1
    )
    tickets = (
        db_session.query(ServiceTicket)
        .filter(ServiceTicket.source == "MAINTENANCE_RISK")
        .all()
    )
    assert len(tickets) == 1
    assert tickets[0].assigned_department == "ENGINEERING"


def test_never_claims_confirmed_failure_language():
    """Guards the PRD hard constraint: without sensors, only 'risk'/'inspection'
    language is used — never a confirmed-failure claim."""
    import inspect

    source = inspect.getsource(risk_service)
    banned = ["is broken", "has failed", "confirmed failure", "hardware failure"]
    for phrase in banned:
        assert phrase not in source.lower()
