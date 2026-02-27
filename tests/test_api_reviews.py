"""Review API tests -- public reads, auth-gated writes."""

import pytest


@pytest.mark.asyncio
async def test_list_reviews_returns_200(client):
    """GET /api/v1/reviews should return 200 with a list."""
    resp = await client.get("/api/v1/reviews")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_review_summary_empty(client):
    """Review summary for nonexistent user should return count 0."""
    resp = await client.get("/api/v1/reviews/summary/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 0
    assert data["average"] is None


@pytest.mark.asyncio
async def test_review_summary_for_user(client):
    """Review summary for a seed user should work."""
    # Get a user from items endpoint
    items_resp = await client.get("/api/v1/items?limit=1")
    items = items_resp.json()
    if items:
        owner_id = items[0]["owner_id"]
        resp = await client.get(f"/api/v1/reviews/summary/{owner_id}")
        assert resp.status_code == 200
        assert "count" in resp.json()
        assert "average" in resp.json()


@pytest.mark.asyncio
async def test_create_review_requires_auth(client):
    """POST /api/v1/reviews should return 401 without auth."""
    resp = await client.post("/api/v1/reviews", json={
        "rental_id": "00000000-0000-0000-0000-000000000000",
        "reviewee_id": "00000000-0000-0000-0000-000000000000",
        "rating": 5,
    })
    assert resp.status_code == 401
