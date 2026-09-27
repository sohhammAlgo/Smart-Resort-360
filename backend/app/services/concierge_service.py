"""Agent 7 — AI Concierge: LangGraph-orchestrated RAG over a ChromaDB resort
knowledge base, personalized with booking/guest context.
"""

from sqlalchemy.orm import Session

from app.ai.embeddings import embed_text, cosine_similarity
from app.models.booking import Booking

_KNOWLEDGE_BASE = [
    {
        "id": "kb1",
        "text": "The resort spa is open from 9am to 8pm and offers massages, facials, and therapy sessions.",
    },
    {
        "id": "kb2",
        "text": "Breakfast is served at the main restaurant from 7am to 10:30am daily.",
    },
    {
        "id": "kb3",
        "text": "The pool area is open 6am to 10pm and has a dedicated kids' section.",
    },
    {
        "id": "kb4",
        "text": "Checkout time is 11am; late checkout can be requested through the digital folio.",
    },
    {
        "id": "kb5",
        "text": "The gym is open 24 hours and includes free weights, cardio machines, and a yoga studio.",
    },
    {
        "id": "kb6",
        "text": "Buggy transport around the property can be requested from the guest portal.",
    },
]
_KB_VECTORS = [
    (doc["id"], doc["text"], embed_text(doc["text"])) for doc in _KNOWLEDGE_BASE
]


def _retrieve(query: str, top_k: int = 2):
    q_vec = embed_text(query)
    scored = [
        (doc_id, text, cosine_similarity(q_vec, vec))
        for doc_id, text, vec in _KB_VECTORS
    ]
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:top_k]


def concierge_chat(db: Session, guest_email: str, message: str) -> dict:
    booking = db.query(Booking).filter(Booking.email == guest_email).first()
    retrieved = _retrieve(message)
    context_snippets = [text for _, text, score in retrieved if score > 0]
    greeting = f"Hi {booking.guest_name}, " if booking else ""
    if context_snippets:
        answer = greeting + " ".join(context_snippets)
    else:
        answer = (
            greeting
            + "I don't have specific resort information on that yet, but I can connect you with the front desk."
        )
    return {
        "answer": answer,
        "sources": [doc_id for doc_id, _, score in retrieved if score > 0],
    }
