"""Bid/auction API tests."""

import pytest


@pytest.mark.asyncio
async def test_place_bid_requires_auth(client):
    """POST /api/v1/bids should require auth."""
    resp = await client.post("/api/v1/bids", json={
        "listing_id": "00000000-0000-0000-0000-000000000001",
        "amount": 10.0,
    })
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_bids_requires_auth(client):
    """GET /api/v1/bids should require auth."""
    resp = await client.get("/api/v1/bids?listing_id=00000000-0000-0000-0000-000000000001")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_auction_summary_not_found(client):
    """GET /api/v1/bids/summary with invalid listing returns 404."""
    resp = await client.get("/api/v1/bids/summary?listing_id=00000000-0000-0000-0000-000000000001")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_end_auction_requires_auth(client):
    """POST /api/v1/bids/{id}/end should require auth."""
    resp = await client.post("/api/v1/bids/00000000-0000-0000-0000-000000000001/end")
    assert resp.status_code in (401, 403)
