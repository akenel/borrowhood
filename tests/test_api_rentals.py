"""Rental API tests -- auth-gated endpoints."""

import pytest


@pytest.mark.asyncio
async def test_list_rentals_requires_auth(client):
    """GET /api/v1/rentals should return 401 without auth."""
    resp = await client.get("/api/v1/rentals")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_rental_requires_auth(client):
    """POST /api/v1/rentals should return 401 without auth."""
    resp = await client.post("/api/v1/rentals", json={
        "listing_id": "00000000-0000-0000-0000-000000000000",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_rental_requires_auth(client):
    """GET /api/v1/rentals/{id} should return 401 without auth."""
    resp = await client.get("/api/v1/rentals/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_rental_status_requires_auth(client):
    """PATCH /api/v1/rentals/{id}/status should return 401 without auth."""
    resp = await client.patch(
        "/api/v1/rentals/00000000-0000-0000-0000-000000000000/status",
        json={"status": "approved"},
    )
    assert resp.status_code == 401
