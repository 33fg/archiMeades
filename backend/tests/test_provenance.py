"""Provenance API tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


def test_provenance_status_returns_json(client: TestClient) -> None:
    """GET /api/provenance/status returns 200 with available and uri."""
    resp = client.get("/api/provenance/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "available" in data
    assert "uri" in data
    assert "bolt://" in data["uri"]


def test_provenance_lineage_requires_neo4j(client: TestClient) -> None:
    """GET /api/provenance/theory/{id}/lineage returns 503 if Neo4j down, else 200."""
    resp = client.get("/api/provenance/theory/fake-id-12345/lineage")
    # Either 503 (Neo4j unavailable) or 200 (Neo4j up, returns empty lineage)
    assert resp.status_code in (200, 503)
    if resp.status_code == 200:
        data = resp.json()
        assert "theory_id" in data or "sim_id" in data or "simulation_ids" in data
