from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_db
from app.services.concierge_service import concierge_chat

router = APIRouter(prefix="/concierge", tags=["concierge"])


class ChatRequest(BaseModel):
    guest_email: str
    message: str


@router.post("/chat")
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    return concierge_chat(db, payload.guest_email, payload.message)
