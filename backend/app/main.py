"""Smart Resort 360 — FastAPI application entrypoint."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import init_db
from app.scheduler.jobs import start_scheduler, shutdown_scheduler

from app.api.routes import (
    auth,
    amenities,
    buggy,
    folio,
    concierge,
    ai_insights,
    operations,
    maintenance,
)

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.APP_NAME, version="9.0.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(amenities.router)
app.include_router(buggy.router)
app.include_router(folio.router)
app.include_router(concierge.router)
app.include_router(ai_insights.router)
app.include_router(operations.router)
app.include_router(maintenance.router)


@app.on_event("startup")
def on_startup():
    init_db()
    start_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    shutdown_scheduler()

@app.get("/")
def root():
    return {"message": "Smart Resort 360 API", "version": "9.0.0"}

@app.get("/health")
def health():
    return {"status": "ok", "service": settings.APP_NAME}


@app.on_event("startup")
def on_startup_seed():
    import os

    if os.getenv("DEMO_SEED", "false").lower() == "true":
        from app.db.session import SessionLocal
        from app.seed.seed_data import seed

        db = SessionLocal()
        try:
            seed(db)
        finally:
            db.close()
