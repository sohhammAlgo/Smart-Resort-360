from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.booking import Booking
from app.models.employee import Employee
from app.schemas.auth import (
    GuestOTPRequest,
    GuestOTPVerify,
    StaffLoginRequest,
    ManagerLoginRequest,
    TokenResponse,
)
from app.services.otp_service import generate_and_send_otp, verify_otp
from app.auth.security import verify_secret, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/guest/request-otp")
def guest_request_otp(payload: GuestOTPRequest, db: Session = Depends(get_db)):
    booking = (
        db.query(Booking)
        .filter(Booking.email == payload.email, Booking.booking_status == "ACTIVE")
        .first()
    )
    if not booking:
        raise HTTPException(
            status_code=404, detail="No active booking found for this email"
        )
    generate_and_send_otp(payload.email)
    return {"message": "OTP sent"}


@router.post("/guest/verify-otp", response_model=TokenResponse)
def guest_verify_otp(payload: GuestOTPVerify, db: Session = Depends(get_db)):
    if not verify_otp(payload.email, payload.otp):
        raise HTTPException(status_code=401, detail="Invalid or expired OTP")
    booking = db.query(Booking).filter(Booking.email == payload.email).first()
    token = create_access_token(
        subject=payload.email, role="GUEST", extra={"booking_id": booking.booking_id}
    )
    return TokenResponse(access_token=token, role="GUEST")


@router.post("/staff/login", response_model=TokenResponse)
def staff_login(payload: StaffLoginRequest, db: Session = Depends(get_db)):
    emp = (
        db.query(Employee)
        .filter(
            Employee.employee_id == payload.employee_id, Employee.is_active.is_(True)
        )
        .first()
    )
    if not emp or not verify_secret(payload.pin, emp.auth_hash):
        raise HTTPException(status_code=401, detail="Invalid employee ID or PIN")
    token = create_access_token(
        subject=emp.employee_id, role=emp.role, extra={"department": emp.department}
    )
    return TokenResponse(access_token=token, role=emp.role)


@router.post("/manager/login", response_model=TokenResponse)
def manager_login(payload: ManagerLoginRequest, db: Session = Depends(get_db)):

    from sqlalchemy import text

    db_name = db.execute(text("SELECT current_database()")).scalar()
    db_schema = db.execute(text("SELECT current_schema()")).scalar()

    print("DATABASE:", db_name)
    print("SCHEMA:", db_schema)

    emp = (
        db.query(Employee)
        .filter(Employee.email == payload.email)
        .first()
    )

    print("EMAIL:", repr(payload.email))
    print("EMP FOUND:", emp is not None)

    if emp:
        print("DB EMAIL:", repr(emp.email))
        print("DB ROLE:", repr(emp.role))

    if not emp or emp.role != "MANAGER":
        raise HTTPException(status_code=401, detail="Manager not found")

    if not verify_secret(payload.password, emp.auth_hash):
        raise HTTPException(status_code=401, detail="Password incorrect")

    token = create_access_token(
        subject=emp.employee_id,
        role="MANAGER"
    )

    return TokenResponse(access_token=token, role="MANAGER")