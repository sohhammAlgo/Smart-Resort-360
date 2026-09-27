import os

os.environ["ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["REDIS_URL"] = "fake://"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["RUN_SCHEDULER"] = "false"
os.environ["AMENITY_OFFER_TTL_SECONDS"] = "2"

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base
from app.db import redis_client


@pytest.fixture(scope="function")
def db_session():
    # StaticPool: a single shared connection, required so that an in-memory
    # SQLite database is visible across threads (used by the concurrency test)
    # instead of each pooled connection getting its own empty :memory: DB.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _fk_pragma(dbapi_con, con_record):
        dbapi_con.execute("PRAGMA foreign_keys=ON")

    from app import models  # noqa: F401 register models

    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(
        bind=engine, autoflush=False, autocommit=False, future=True
    )
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def _fresh_fake_redis():
    redis_client._client = None
    yield
    redis_client._client = None
