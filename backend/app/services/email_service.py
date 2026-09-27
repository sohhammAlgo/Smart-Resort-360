import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_otp_email(to_email: str, otp: str, ttl_seconds: int) -> None:
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_username = settings.SMTP_USER
    smtp_password = settings.SMTP_PASSWORD
    smtp_from = settings.SMTP_FROM or smtp_username

    if not smtp_host:
        raise RuntimeError("SMTP_HOST is not configured")

    if not smtp_username:
        raise RuntimeError("SMTP_USER is not configured")

    if not smtp_password:
        raise RuntimeError("SMTP_PASSWORD is not configured")

    message = EmailMessage()

    message["Subject"] = "Your Smart Resort 360 OTP"
    message["From"] = smtp_from
    message["To"] = to_email

    validity = (
        f"{ttl_seconds // 60} minutes"
        if ttl_seconds % 60 == 0
        else f"{ttl_seconds} seconds"
    )
    message.set_content(
        f"""
Hello,

Your Smart Resort 360 verification OTP is:

{otp}

This OTP will expire in {validity}.

If you did not request this OTP, you can ignore this email.

Regards,
Smart Resort 360
"""
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(message)