"""Deposit API tests."""

import pytest


@pytest.mark.asyncio
async def test_hold_deposit_requires_auth(client):
    """POST /api/v1/deposits should require auth."""
    resp = await client.post("/api/v1/deposits", json={
        "rental_id": "00000000-0000-0000-0000-000000000001",
        "amount": 50.0,
    })
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_deposits_requires_auth(client):
    """GET /api/v1/deposits should require auth."""
    resp = await client.get("/api/v1/deposits")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_release_deposit_requires_auth(client):
    """PATCH /api/v1/deposits/{id}/release should require auth."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = await client.patch(f"/api/v1/deposits/{fake_id}/release", json={})
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_forfeit_deposit_requires_auth(client):
    """PATCH /api/v1/deposits/{id}/forfeit should require auth."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = await client.patch(f"/api/v1/deposits/{fake_id}/forfeit", json={
        "reason": "Item was damaged beyond repair.",
    })
    assert resp.status_code in (401, 403)
