"""Service tickets — the operational task queue used by the Autonomous Department
Head, preventive maintenance (Phase 9A) and NLP routing (F11).
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models.ticket import ServiceTicket
from app.models.employee import Employee

SLA_HOURS_BY_URGENCY = {"LOW": 24, "MEDIUM": 8, "HIGH": 2}


def create_ticket(
    db: Session,
    location: str,
    issue_category: str,
    department: str,
    guest_id: str | None = None,
    urgency: str = "MEDIUM",
    source: str = "MANUAL",
) -> ServiceTicket:
    employee = (
        db.query(Employee)
        .filter(Employee.department == department, Employee.is_active.is_(True))
        .first()
    )
    sla_hours = SLA_HOURS_BY_URGENCY.get(urgency, 8)
    ticket = ServiceTicket(
        guest_id=guest_id,
        location=location,
        issue_category=issue_category,
        assigned_department=department,
        assigned_employee_id=employee.employee_id if employee else None,
        status="OPEN",
        source=source,
        sla_deadline=datetime.now(timezone.utc) + timedelta(hours=sla_hours),
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_ticket_status(db: Session, ticket_id: int, status: str) -> ServiceTicket:
    ticket = db.query(ServiceTicket).get(ticket_id)
    if not ticket:
        raise ValueError("Ticket not found")
    ticket.status = status
    db.commit()
    db.refresh(ticket)
    return ticket
