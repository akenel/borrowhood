"""Health endpoint tests."""

import pytest


@pytest.mark.asyncio
async def test_health_returns_200(client):
    """Health check should return 200 with app info."""
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["app"] == "La Piazza"
    assert data["version"] == "1.0.0"
    assert data["status"] in ("healthy", "degraded")
    assert "checks" in data
    assert "database" in data["checks"]


@pytest.mark.asyncio
async def test_health_has_timestamp(client):
    """Health check should include ISO timestamp."""
    resp = await client.get("/api/v1/health")
    data = resp.json()
    assert "timestamp" in data
    assert "T" in data["timestamp"]  # ISO format


@pytest.mark.asyncio
async def test_health_has_uptime(client):
    """Health check should include uptime counter."""
    resp = await client.get("/api/v1/health")
    data = resp.json()
    assert "uptime_seconds" in data
    assert isinstance(data["uptime_seconds"], int)
