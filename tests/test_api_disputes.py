"""Dispute API tests."""

import pytest


@pytest.mark.asyncio
async def test_file_dispute_requires_auth(client):
    """POST /api/v1/disputes should require auth."""
    resp = await client.post("/api/v1/disputes", json={
        "rental_id": "00000000-0000-0000-0000-000000000001",
        "reason": "item_damaged",
        "description": "The item was damaged when I received it.",
    })
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_disputes_requires_auth(client):
    """GET /api/v1/disputes should require auth."""
    resp = await client.get("/api/v1/disputes")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_dispute_summary_requires_auth(client):
    """GET /api/v1/disputes/summary should require auth."""
    resp = await client.get("/api/v1/disputes/summary")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_respond_dispute_requires_auth(client):
    """PATCH /api/v1/disputes/{id}/respond should require auth."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = await client.patch(f"/api/v1/disputes/{fake_id}/respond", json={
        "response": "I disagree with this dispute claim.",
    })
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_resolve_dispute_requires_auth(client):
    """PATCH /api/v1/disputes/{id}/resolve should require auth."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = await client.patch(f"/api/v1/disputes/{fake_id}/resolve", json={
        "resolution": "full_refund",
    })
    assert resp.status_code in (401, 403)
