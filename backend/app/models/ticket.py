from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime, timezone
from app.db.session import Base


class ServiceTicket(Base):
    __tablename__ = "service_tickets"

    ticket_id = Column(Integer, primary_key=True, autoincrement=True)
    guest_id = Column(String(50), nullable=True)
    location = Column(String(100), nullable=False)
    issue_category = Column(String(50), nullable=False)
    assigned_department = Column(String(50), nullable=False)
    assigned_employee_id = Column(
        String(20), ForeignKey("employees.employee_id"), nullable=True
    )
    status = Column(String(20), default="OPEN")
    source = Column(
        String(30), default="MANUAL"
    )  # MANUAL, MAINTENANCE_RISK, NLP_ROUTING
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    sla_deadline = Column(DateTime, nullable=False)
