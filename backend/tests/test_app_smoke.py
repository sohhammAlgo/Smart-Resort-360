"""Smoke tests: app boots, OpenAPI schema is valid, health check works."""

import os

os.environ.setdefault("DEMO_SEED", "false")
from fastapi.testclient import TestClient
from app.main import app


def test_health_check():
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"


def test_openapi_schema_generates():
    schema = app.openapi()
    assert schema["info"]["title"] == "Smart Resort 360"
    assert "/amenities" in schema["paths"]
    assert "/maintenance/{asset_id}/evaluate" in schema["paths"]
