"""Tests for theory registration and validation - WO-21."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def valid_code():
    """Theory code with required methods."""
    return """
def luminosity_distance(z):
    return 1.0

def age_of_universe():
    return 13.8
"""


@pytest.fixture
def invalid_code():
    """Theory code missing required methods."""
    return "def foo(): pass"


@pytest.mark.asyncio
async def test_register_invalid_interface_fails(invalid_code):
    """POST /register with invalid code returns 422."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        r = await client.post(
            "/api/theories/register",
            json={"identifier": "bad", "version": "1.0", "code": invalid_code},
        )
    assert r.status_code == 422
    data = r.json()
    assert "missing_methods" in data
    assert "luminosity_distance" in data["missing_methods"]
    assert "age_of_universe" in data["missing_methods"]


@pytest.mark.asyncio
async def test_register_valid_returns_202(valid_code):
    """POST /register with valid code returns 202 and status_url."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        r = await client.post(
            "/api/theories/register",
            json={"identifier": "test_valid", "version": "1.0", "code": valid_code},
        )
    assert r.status_code == 202
    data = r.json()
    assert "theory_id" in data
    assert "status_url" in data
    assert "validation-status" in data["status_url"]
