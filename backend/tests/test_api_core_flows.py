"""API-level tests for preserved Phase 0-8 flows: auth, buggy, folio/checkout,
tickets, and emergency — exercised through the FastAPI TestClient."""

from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db
from app.models.employee import Employee
from app.models.booking import Booking
from app.models.otp import OTPVerification
from app.auth.security import hash_secret


@pytest.fixture
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_staff_login_success_and_failure(client, db_session):
    db_session.add(
        Employee(
            employee_id="TRN001",
            full_name="Driver",
            role="STAFF",
            department="TRANSPORT",
            email="d@x.com",
            auth_hash=hash_secret("4321"),
        )
    )
    db_session.commit()

    resp = client.post(
        "/auth/staff/login", json={"employee_id": "TRN001", "pin": "4321"}
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "STAFF"

    bad = client.post(
        "/auth/staff/login", json={"employee_id": "TRN001", "pin": "wrong"}
    )
    assert bad.status_code == 401


def test_guest_otp_requires_active_booking(client, db_session, monkeypatch):
    sent_otps = []
    generated_otps = iter(("1234", "5678", "9012", "3456"))
    monkeypatch.setattr(
        "app.services.otp_service.generate_otp",
        lambda: next(generated_otps),
    )
    monkeypatch.setattr(
        "app.services.otp_service.send_otp_email",
        lambda email, otp, ttl_seconds: sent_otps.append(otp),
    )

    resp = client.post("/auth/guest/request-otp", json={"email": "nobody@example.com"})
    assert resp.status_code == 404

    db_session.add(
        Booking(
            guest_name="Test Guest",
            email="guest@example.com",
            room_number="201",
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=2),
        )
    )
    db_session.commit()
    resp2 = client.post("/auth/guest/request-otp", json={"email": "guest@example.com"})
    assert resp2.status_code == 200
    first_otp = sent_otps[-1]
    assert len(first_otp) == 4
    assert db_session.query(OTPVerification).filter_by(otp=first_otp).one()

    invalid = client.post(
        "/auth/guest/verify-otp",
        json={"email": "guest@example.com", "otp": "0000"},
    )
    assert invalid.status_code == 401

    resp3 = client.post("/auth/guest/request-otp", json={"email": "guest@example.com"})
    assert resp3.status_code == 200
    newest_otp = sent_otps[-1]
    assert newest_otp != first_otp

    old_code = client.post(
        "/auth/guest/verify-otp",
        json={"email": "guest@example.com", "otp": first_otp},
    )
    assert old_code.status_code == 401

    verified = client.post(
        "/auth/guest/verify-otp",
        json={"email": "guest@example.com", "otp": newest_otp},
    )
    assert verified.status_code == 200

    reused = client.post(
        "/auth/guest/verify-otp",
        json={"email": "guest@example.com", "otp": newest_otp},
    )
    assert reused.status_code == 401

    assert client.post(
        "/auth/guest/request-otp", json={"email": "guest@example.com"}
    ).status_code == 200
    expired_otp = sent_otps[-1]
    expired_record = (
        db_session.query(OTPVerification).filter_by(otp=expired_otp).one()
    )
    expired_record.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    db_session.commit()
    expired = client.post(
        "/auth/guest/verify-otp",
        json={"email": "guest@example.com", "otp": expired_otp},
    )
    assert expired.status_code == 401

    def fail_email(email, otp, ttl_seconds):
        raise RuntimeError("SMTP unavailable")

    monkeypatch.setattr("app.services.otp_service.send_otp_email", fail_email)
    email_failure = client.post(
        "/auth/guest/request-otp", json={"email": "guest@example.com"}
    )
    assert email_failure.status_code == 502
    assert (
        db_session.query(OTPVerification)
        .filter_by(email="guest@example.com", verified=False)
        .count()
        == 0
    )


def test_buggy_request_flow(client, db_session):
    db_session.add(
        Employee(
            employee_id="TRN002",
            full_name="Driver2",
            role="STAFF",
            department="TRANSPORT",
            email="d2@x.com",
            auth_hash=hash_secret("1"),
        )
    )
    db_session.commit()
    resp = client.post(
        "/buggy/request",
        json={
            "guest_id": "guest-1",
            "pickup_location": "Lobby",
            "dropoff_location": "Spa",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ASSIGNED"

    got = client.get(f"/buggy/{body['request_id']}")
    assert got.status_code == 200


def test_folio_charge_list_and_checkout(client, db_session):
    booking = Booking(
        guest_name="Folio Guest",
        email="folio@example.com",
        room_number="301",
        check_in_date=date.today(),
        check_out_date=date.today() + timedelta(days=1),
    )
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)

    client.post(
        "/folio/charge",
        json={
            "booking_id": booking.booking_id,
            "room_number": "301",
            "category": "SPA",
            "description": "Massage",
            "amount": "50.00",
        },
    )
    listing = client.get("/folio", params={"booking_id": booking.booking_id})
    assert listing.status_code == 200
    assert len(listing.json()) == 1

    checkout = client.post("/checkout", params={"booking_id": booking.booking_id})
    assert checkout.status_code == 200
    assert checkout.json()["status"] == "CHECKED_OUT"


def test_ticket_and_emergency_endpoints(client, db_session):
    db_session.add(
        Employee(
            employee_id="ENG02",
            full_name="Eng2",
            role="ENGINEERING",
            department="ENGINEERING",
            email="eng2@x.com",
            auth_hash=hash_secret("1"),
        )
    )
    db_session.commit()

    resp = client.post(
        "/tickets",
        json={
            "location": "Room 5",
            "issue_category": "leak",
            "department": "ENGINEERING",
            "urgency": "HIGH",
        },
    )
    assert resp.status_code == 200
    ticket_id = resp.json()["ticket_id"]

    patched = client.patch(f"/tickets/{ticket_id}", json={"status": "RESOLVED"})
    assert patched.status_code == 200
    assert patched.json()["status"] == "RESOLVED"

    sos = client.post(
        "/emergency/sos",
        json={
            "initiator_role": "GUEST",
            "location": "Pool",
            "alert_type": "MEDICAL",
            "message": "Guest fainted",
        },
    )
    assert sos.status_code == 200

    broadcast = client.post(
        "/emergency/broadcast", json={"manager_id": "MGR001", "message": "Evacuate now"}
    )
    assert broadcast.status_code == 200


def test_amenity_waitlist_offer_accept_flow_via_api(client, db_session):
    from app.models.amenity import Amenity

    amenity = Amenity(name="Sauna", category="SAUNA", status="FREE", capacity=2)
    db_session.add(amenity)
    db_session.commit()
    db_session.refresh(amenity)

    listing = client.get("/amenities")
    assert listing.status_code == 200

    joined = client.post(
        f"/amenities/{amenity.id}/waitlist", json={"guest_id": "guest-9"}
    )
    assert joined.status_code == 200

    from app.models.amenity_offer import AmenityOffer

    offer = (
        db_session.query(AmenityOffer)
        .filter(AmenityOffer.amenity_id == amenity.id)
        .first()
    )
    assert offer is not None

    accepted = client.post(f"/amenities/{amenity.id}/offers/{offer.offer_id}/accept")
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "ACCEPTED"
