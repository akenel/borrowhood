"""Item API tests -- public list and get endpoints.

Uses db_client fixture which auto-skips if database is not reachable.
"""

import pytest


@pytest.mark.asyncio
async def test_list_items_returns_200(db_client):
    """GET /api/v1/items should return 200 with a list."""
    resp = await db_client.get("/api/v1/items")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_items_has_seed_data(db_client):
    """Items list should contain seed data."""
    resp = await db_client.get("/api/v1/items")
    items = resp.json()
    assert len(items) > 0
    for item in items:
        assert "id" in item
        assert "name" in item
        assert "slug" in item
        assert "item_type" in item
        assert "category" in item


@pytest.mark.asyncio
async def test_list_items_search(db_client):
    """Items search should filter by name/description."""
    resp = await db_client.get("/api/v1/items?q=cookie")
    items = resp.json()
    assert len(items) > 0
    assert any("cookie" in item["name"].lower() for item in items)


@pytest.mark.asyncio
async def test_list_items_filter_category(db_client):
    """Items filter by category."""
    resp = await db_client.get("/api/v1/items?category=kitchen")
    items = resp.json()
    for item in items:
        assert item["category"] == "kitchen"


@pytest.mark.asyncio
async def test_list_items_sort_oldest(db_client):
    """Items sorted by oldest should work."""
    resp = await db_client.get("/api/v1/items?sort=oldest")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_items_pagination(db_client):
    """Items pagination with limit and offset."""
    resp = await db_client.get("/api/v1/items?limit=2&offset=0")
    items = resp.json()
    assert len(items) <= 2


@pytest.mark.asyncio
async def test_get_item_by_id(db_client):
    """GET /api/v1/items/{id} should return a single item."""
    resp = await db_client.get("/api/v1/items?limit=1")
    items = resp.json()
    assert len(items) > 0

    item_id = items[0]["id"]
    resp = await db_client.get(f"/api/v1/items/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == item_id


@pytest.mark.asyncio
async def test_get_item_404(db_client):
    """GET /api/v1/items/{id} should return 404 for nonexistent."""
    resp = await db_client.get("/api/v1/items/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_item_requires_auth(client):
    """POST /api/v1/items should return 401 without auth."""
    resp = await client.post("/api/v1/items", json={
        "name": "Test Item",
        "item_type": "physical",
        "category": "tools",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_delete_item_requires_auth(db_client):
    """DELETE /api/v1/items/{id} should return 401 without auth."""
    resp = await db_client.get("/api/v1/items?limit=1")
    item_id = resp.json()[0]["id"]
    resp = await db_client.delete(f"/api/v1/items/{item_id}")
    assert resp.status_code == 401
