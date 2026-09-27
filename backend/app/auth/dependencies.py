"""RBAC dependencies for FastAPI routes."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.auth.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/staff/login", auto_error=False)


class CurrentUser:
    def __init__(self, subject: str, role: str, claims: dict):
        self.subject = subject
        self.role = role
        self.claims = claims


def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )
    return CurrentUser(subject=payload["sub"], role=payload["role"], claims=payload)


def require_roles(*allowed_roles: str):
    def _checker(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role permissions",
            )
        return user

    return _checker


require_guest = require_roles("GUEST")
require_staff = require_roles("STAFF", "ENGINEERING", "MANAGER")
require_engineering = require_roles("ENGINEERING", "MANAGER")
require_manager = require_roles("MANAGER")
