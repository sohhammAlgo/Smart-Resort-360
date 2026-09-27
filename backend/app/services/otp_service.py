"""Guest OTP: 4-digit code, Redis TTL, delivered via smtplib with a dev-console fallback."""

import random
import smtplib
import logging
from email.mime.text import MIMEText

from app.core.config import settings
from app.db.redis_client import get_redis

logger = logging.getLogger("otp_service")


def _otp_key(email: str) -> str:
    return f"otp:{email.lower()}"


def generate_and_send_otp(email: str) -> str:
    otp = "".join(random.choices("0123456789", k=settings.OTP_LENGTH))
    get_redis().setex(_otp_key(email), settings.OTP_TTL_SECONDS, otp)
    _send_email(email, otp)
    return otp


def verify_otp(email: str, otp: str) -> bool:
    key = _otp_key(email)
    stored = get_redis().get(key)
    if stored is None:
        return False
    if stored == otp:
        get_redis().delete(key)
        return True
    return False


def _send_email(email: str, otp: str):
    subject = "Your Smart Resort 360 login code"
    body = f"Your one-time login code is {otp}. It expires in {settings.OTP_TTL_SECONDS // 60} minutes."
    if not settings.SMTP_HOST:
        if settings.EMAIL_DEV_CONSOLE_FALLBACK:
            logger.info("DEV EMAIL FALLBACK -> to=%s otp=%s", email, otp)
            return
        raise RuntimeError("SMTP not configured and dev console fallback disabled")
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = email
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.starttls()
            if settings.SMTP_USER:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, [email], msg.as_string())
    except Exception as exc:  # pragma: no cover - network dependent
        logger.warning("SMTP send failed (%s); falling back to dev console log", exc)
        logger.info("DEV EMAIL FALLBACK -> to=%s otp=%s", email, otp)
