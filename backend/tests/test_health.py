"""Health endpoint tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


def test_health_returns_ok(client: TestClient) -> None:
    """GET /health returns 200 with status ok or degraded."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") in ("ok", "degraded")  # degraded when Redis/S3 unavailable
    assert data.get("database") in ("ok", "unavailable")
    assert data.get("redis") in ("ok", "unavailable")
    assert data.get("s3") in ("ok", "unavailable")
