"""Demo/seed data for Phase 9D end-to-end demonstration and local development."""

from datetime import date, timedelta
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.booking import Booking
from app.models.amenity import Amenity
from app.models.asset import Asset
from app.models.maintenance import MaintenanceHistory
from app.auth.security import hash_secret
from app.services.recommendation_service import index_all_amenities


def seed(db: Session):
    employees_to_seed = [
        {
            "employee_id": "ENG001",
            "full_name": "Ravi Shah",
            "role": "ENGINEERING",
            "department": "ENGINEERING",
            "email": "ravi.eng@smartresort360.com",
            "password": "1234",
        },
        {
            "employee_id": "TRN001",
            "full_name": "Meera Nair",
            "role": "STAFF",
            "department": "TRANSPORT",
            "email": "meera.transport@smartresort360.com",
            "password": "1234",
        },
        {
            "employee_id": "MGR001",
            "full_name": "Ananya Rao",
            "role": "MANAGER",
            "department": "MANAGEMENT",
            "email": "ananya.manager@smartresort360.com",
            "password": "Manager@123",
        },
    ]

    for item in employees_to_seed:
        emp = db.query(Employee).filter(Employee.employee_id == item["employee_id"]).first()
        if not emp:
            emp = db.query(Employee).filter(Employee.email == item["email"]).first()
        
        hashed = hash_secret(item["password"])
        if not emp:
            emp = Employee(
                employee_id=item["employee_id"],
                full_name=item["full_name"],
                role=item["role"],
                department=item.get("department") or item.get("department="),
                email=item["email"],
                auth_hash=hashed,
                is_active=True,
            )
            db.add(emp)
        else:
            emp.full_name = item["full_name"]
            emp.role = item["role"]
            emp.department = item.get("department") or item.get("department=")
            emp.email = item["email"]
            emp.auth_hash = hashed
            emp.is_active = True
    db.commit()

    if db.query(Booking).count() == 0:
        today = date.today()
        db.add_all(
            [
                Booking(
                    guest_name="Aarav Mehta",
                    email="aarav@example.com",
                    room_number="101",
                    check_in_date=today - timedelta(days=1),
                    check_out_date=today + timedelta(days=3),
                ),
                Booking(
                    guest_name="Diya Kapoor",
                    email="diya@example.com",
                    room_number="102",
                    check_in_date=today - timedelta(days=2),
                    check_out_date=today + timedelta(days=2),
                ),
            ]
        )

    if db.query(Amenity).count() == 0:
        db.add_all(
            [
                Amenity(
                    name="Spa",
                    category="SPA",
                    status="FREE",
                    capacity=2,
                    description="Full-service spa with massage and therapy rooms",
                ),
                Amenity(
                    name="Sauna",
                    category="SAUNA",
                    status="FREE",
                    capacity=4,
                    description="Steam and dry sauna room",
                ),
                Amenity(
                    name="Yoga Studio",
                    category="YOGA",
                    status="FREE",
                    capacity=10,
                    description="Guided yoga and meditation sessions",
                ),
                Amenity(
                    name="Main Pool",
                    category="POOL",
                    status="FREE",
                    capacity=20,
                    description="Outdoor swimming pool",
                ),
                Amenity(
                    name="Fitness Gym",
                    category="GYM",
                    status="FREE",
                    capacity=15,
                    description="Gym with weights and cardio machines",
                ),
            ]
        )
    db.commit()

    spa = db.query(Amenity).filter(Amenity.name == "Spa").first()
    if spa and db.query(Asset).filter(Asset.linked_amenity_id == spa.id).count() == 0:
        asset = Asset(
            asset_type="HVAC_UNIT",
            room_or_location="Spa",
            installation_date=date.today() - timedelta(days=3000),
            last_service_date=date.today() - timedelta(days=400),
            service_interval_days=180,
            linked_amenity_id=spa.id,
        )
        db.add(asset)
        db.commit()
        db.refresh(asset)
        db.add_all(
            [
                MaintenanceHistory(
                    asset_id=asset.asset_id,
                    issue_type="AC_NOISE",
                    severity="MEDIUM",
                    is_complaint=1,
                ),
                MaintenanceHistory(
                    asset_id=asset.asset_id,
                    issue_type="AC_NOISE",
                    severity="HIGH",
                    is_complaint=1,
                ),
            ]
        )
        db.commit()

    index_all_amenities(db)
