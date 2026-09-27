from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.models.ticket import ServiceTicket
from app.services.ticket_service import create_ticket, update_ticket_status
from app.services.emergency_service import create_sos, broadcast_emergency

router = APIRouter(tags=["operations"])


class TicketIn(BaseModel):
    location: str
    issue_category: str
    department: str
    guest_id: str | None = None
    urgency: str = "MEDIUM"


@router.post("/tickets")
def post_ticket(payload: TicketIn, db: Session = Depends(get_db)):
    ticket = create_ticket(
        db,
        payload.location,
        payload.issue_category,
        payload.department,
        payload.guest_id,
        payload.urgency,
    )
    return {
        "ticket_id": ticket.ticket_id,
        "status": ticket.status,
        "assigned_employee_id": ticket.assigned_employee_id,
    }


@router.get("/tickets")
def list_tickets(db: Session = Depends(get_db)):
    rows = db.query(ServiceTicket).all()
    return [
        {
            "ticket_id": t.ticket_id,
            "location": t.location,
            "status": t.status,
            "source": t.source,
        }
        for t in rows
    ]


class TicketPatch(BaseModel):
    status: str


@router.patch("/tickets/{ticket_id}")
def patch_ticket(ticket_id: int, payload: TicketPatch, db: Session = Depends(get_db)):
    try:
        ticket = update_ticket_status(db, ticket_id, payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"ticket_id": ticket.ticket_id, "status": ticket.status}


class SosIn(BaseModel):
    initiator_role: str
    location: str
    alert_type: str
    message: str


@router.post("/emergency/sos")
def sos(payload: SosIn, db: Session = Depends(get_db)):
    alert = create_sos(
        db,
        payload.initiator_role,
        payload.location,
        payload.alert_type,
        payload.message,
    )
    return {"alert_id": alert.alert_id}


class BroadcastIn(BaseModel):
    manager_id: str
    message: str
    location: str = "PROPERTY_WIDE"


@router.post("/emergency/broadcast")
def broadcast(payload: BroadcastIn, db: Session = Depends(get_db)):
    alert = broadcast_emergency(
        db, payload.manager_id, payload.message, payload.location
    )
    return {"alert_id": alert.alert_id}
