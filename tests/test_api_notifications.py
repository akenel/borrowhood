"""Notification API tests -- all endpoints require authentication."""

import pytest


@pytest.mark.asyncio
async def test_notification_summary_requires_auth(client):
    """GET /api/v1/notifications/summary should require auth."""
    resp = await client.get("/api/v1/notifications/summary")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_notifications_requires_auth(client):
    """GET /api/v1/notifications should require auth."""
    resp = await client.get("/api/v1/notifications")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_mark_read_requires_auth(client):
    """PATCH /api/v1/notifications/{id}/read should require auth."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = await client.patch(f"/api/v1/notifications/{fake_id}/read")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_mark_all_read_requires_auth(client):
    """POST /api/v1/notifications/read-all should require auth."""
    resp = await client.post("/api/v1/notifications/read-all")
    assert resp.status_code in (401, 403)
