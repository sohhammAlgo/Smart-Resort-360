from pydantic import BaseModel, EmailStr


class GuestOTPRequest(BaseModel):
    email: EmailStr


class GuestOTPVerify(BaseModel):
    email: EmailStr
    otp: str


class StaffLoginRequest(BaseModel):
    employee_id: str
    pin: str


class ManagerLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
