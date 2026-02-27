"""Listing API tests -- public list and get endpoints."""

import pytest


@pytest.mark.asyncio
async def test_list_listings_returns_200(client):
    """GET /api/v1/listings should return 200 with a list."""
    resp = await client.get("/api/v1/listings")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_listings_has_seed_data(client):
    """Listings should contain seed data."""
    resp = await client.get("/api/v1/listings")
    listings = resp.json()
    assert len(listings) > 0
    for listing in listings:
        assert "id" in listing
        assert "item_id" in listing
        assert "listing_type" in listing
        assert "status" in listing


@pytest.mark.asyncio
async def test_list_listings_filter_by_item(client):
    """Listings filter by item_id."""
    # Get an item first
    items_resp = await client.get("/api/v1/items?limit=1")
    item_id = items_resp.json()[0]["id"]

    resp = await client.get(f"/api/v1/listings?item_id={item_id}")
    assert resp.status_code == 200
    for listing in resp.json():
        assert listing["item_id"] == item_id


@pytest.mark.asyncio
async def test_get_listing_by_id(client):
    """GET /api/v1/listings/{id} should return a single listing."""
    resp = await client.get("/api/v1/listings?limit=1")
    listings = resp.json()
    assert len(listings) > 0

    listing_id = listings[0]["id"]
    resp = await client.get(f"/api/v1/listings/{listing_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == listing_id


@pytest.mark.asyncio
async def test_get_listing_404(client):
    """GET /api/v1/listings/{id} should return 404 for nonexistent."""
    resp = await client.get("/api/v1/listings/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_listing_requires_auth(client):
    """POST /api/v1/listings should return 401 without auth."""
    resp = await client.post("/api/v1/listings", json={
        "item_id": "00000000-0000-0000-0000-000000000000",
        "listing_type": "rent",
    })
    assert resp.status_code == 401
