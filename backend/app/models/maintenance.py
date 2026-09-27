from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric
from datetime import datetime, timezone
from app.db.session import Base


class MaintenanceHistory(Base):
    __tablename__ = "maintenance_history"

    maintenance_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"))
    issue_type = Column(String(100), nullable=True)
    severity = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH
    inspected_at = Column(DateTime, nullable=True)
    repaired_at = Column(DateTime, nullable=True)
    technician_id = Column(
        String(20), ForeignKey("employees.employee_id"), nullable=True
    )
    notes = Column(Text, nullable=True)
    # Also captures guest complaints tied to this asset, used as a risk-scoring input.
    is_complaint = Column(
        Integer, default=0
    )  # 0/1 flag; kept simple/portable across DB backends


class MaintenanceRisk(Base):
    __tablename__ = "maintenance_risk"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"))
    risk_score = Column(Numeric(5, 2), nullable=False)
    risk_level = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH
    model_or_rule_version = Column(String(50), nullable=False)
    # Transparent breakdown of the weighted score, stored for auditability.
    score_breakdown_json = Column(Text, nullable=True)
    calculated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
