import hmac
import logging
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.otp import OTPVerification
from app.services.email_service import send_otp_email

logger = logging.getLogger(__name__)


class OTPEmailDeliveryError(Exception):
    pass


def generate_otp() -> str:
    return f"{secrets.randbelow(10 ** settings.OTP_LENGTH):0{settings.OTP_LENGTH}d}"


def create_and_send_otp(db: Session, email: str) -> None:
    logger.info("OTP generation started")
    email = email.strip().lower()
    otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=settings.OTP_TTL_SECONDS
    )

    db.execute(
        delete(OTPVerification).where(
            OTPVerification.email == email,
            OTPVerification.verified.is_(False),
        )
    )
    otp_record = OTPVerification(
        email=email,
        otp=otp,
        expires_at=expires_at,
        verified=False,
    )

    db.add(otp_record)
    db.commit()
    logger.info("OTP stored successfully for %s", email)

    try:
        logger.info("Sending OTP email to %s", email)
        send_otp_email(email, otp, settings.OTP_TTL_SECONDS)
    except Exception as exc:
        logger.error("OTP email failed: %s: %s", type(exc).__name__, exc)
        db.delete(otp_record)
        db.commit()
        raise OTPEmailDeliveryError("OTP email delivery failed") from exc

    logger.info("OTP email sent successfully to %s", email)


def verify_otp(db: Session, email: str, otp: str) -> bool:
    email = email.strip().lower()
    otp_record = db.execute(
        select(OTPVerification)
        .where(
            OTPVerification.email == email,
            OTPVerification.verified.is_(False),
        )
        .order_by(OTPVerification.created_at.desc(), OTPVerification.id.desc())
        .limit(1)
    ).scalar_one_or_none()

    if otp_record is None or not hmac.compare_digest(otp_record.otp, otp):
        return False

    now = datetime.now(timezone.utc)
    expires_at = otp_record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        db.execute(
            update(OTPVerification)
            .where(
                OTPVerification.email == email,
                OTPVerification.verified.is_(False),
            )
            .values(verified=True)
        )
        db.commit()
        return False

    db.execute(
        update(OTPVerification)
        .where(
            OTPVerification.email == email,
            OTPVerification.verified.is_(False),
        )
        .values(verified=True)
    )
    db.commit()
    return True