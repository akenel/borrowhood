"""Badge API tests."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_badge_catalog_public(client: AsyncClient):
    """Badge catalog is publicly accessible."""
    resp = await client.get("/api/v1/badges/catalog")
    assert resp.status_code == 200
    badges = resp.json()
    assert len(badges) >= 10  # We defined 14 badges
    assert all("code" in b and "name" in b for b in badges)


@pytest.mark.asyncio
async def test_list_badges_requires_auth(client: AsyncClient):
    """Listing own badges requires authentication."""
    resp = await client.get("/api/v1/badges")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_check_badges_requires_auth(client: AsyncClient):
    """Badge check requires authentication."""
    resp = await client.post("/api/v1/badges/check")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_user_badges_public(client: AsyncClient):
    """User badges endpoint is publicly accessible (returns empty for unknown user)."""
    from uuid import uuid4
    resp = await client.get(f"/api/v1/badges/user/{uuid4()}")
    assert resp.status_code == 200
    assert resp.json() == []
