from pydantic import BaseModel
from typing import Optional
from datetime import date


class AssetCreate(BaseModel):
    asset_type: str
    room_or_location: str
    installation_date: Optional[date] = None
    last_service_date: Optional[date] = None
    service_interval_days: Optional[int] = None
    linked_amenity_id: Optional[int] = None


class AssetOut(AssetCreate):
    asset_id: int
    status: str

    class Config:
        from_attributes = True


class MaintenanceHistoryCreate(BaseModel):
    asset_id: int
    issue_type: Optional[str] = None
    severity: Optional[str] = None
    technician_id: Optional[str] = None
    notes: Optional[str] = None
    is_complaint: int = 0


class RiskBreakdown(BaseModel):
    service_overdue_score: float
    asset_age_score: float
    usage_score: float
    previous_failures_score: float
    complaints_score: float
    weights: dict


class RiskOut(BaseModel):
    asset_id: int
    risk_score: float
    risk_level: str
    breakdown: RiskBreakdown
    model_or_rule_version: str
