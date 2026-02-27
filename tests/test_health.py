"""Health endpoint tests."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import create_app


@pytest.mark.asyncio
async def test_health_returns_200():
    """Health check should return 200 with app info."""
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as client:
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["app"] == "BorrowHood"
        assert data["version"] == "1.0.0"
        assert "checks" in data
