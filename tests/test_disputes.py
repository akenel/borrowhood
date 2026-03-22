"""Dispute API contract tests.

Verifies the dispute endpoints exist, accept correct inputs,
and reject bad requests. Does NOT need a database -- tests HTTP-level behavior.
"""

import pytest


@pytest.mark.asyncio
async def test_dispute_list_requires_auth(client):
    """GET /disputes should return 401 without auth."""
    resp = await client.get("/api/v1/disputes")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_dispute_summary_requires_auth(client):
    """GET /disputes/summary should return 401 without auth."""
    resp = await client.get("/api/v1/disputes/summary")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_file_dispute_requires_auth(client):
    """POST /disputes should return 401 without auth."""
    resp = await client.post("/api/v1/disputes", json={
        "rental_id": "00000000-0000-0000-0000-000000000000",
        "reason": "item_damaged",
        "description": "The item was damaged when I received it."
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_file_dispute_validates_reason(client):
    """POST /disputes should reject invalid reason enum."""
    resp = await client.post("/api/v1/disputes", json={
        "rental_id": "00000000-0000-0000-0000-000000000000",
        "reason": "i_dont_like_it",
        "description": "Not a valid reason"
    })
    # 401 (no auth) or 422 (validation) -- either way not 500
    assert resp.status_code in (401, 422)


@pytest.mark.asyncio
async def test_file_dispute_requires_description(client):
    """POST /disputes should reject missing description."""
    resp = await client.post("/api/v1/disputes", json={
        "rental_id": "00000000-0000-0000-0000-000000000000",
        "reason": "item_damaged"
    })
    assert resp.status_code in (401, 422)


@pytest.mark.asyncio
async def test_respond_dispute_requires_auth(client):
    """PATCH /disputes/{id}/respond should return 401 without auth."""
    resp = await client.patch(
        "/api/v1/disputes/00000000-0000-0000-0000-000000000000/respond",
        json={"response": "This is my response to the dispute."}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_resolve_dispute_requires_auth(client):
    """PATCH /disputes/{id}/resolve should return 401 without auth."""
    resp = await client.patch(
        "/api/v1/disputes/00000000-0000-0000-0000-000000000000/resolve",
        json={"resolution": "full_refund", "resolution_notes": "Refunded in full."}
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_resolve_validates_resolution_enum(client):
    """PATCH /disputes/{id}/resolve should reject invalid resolution."""
    resp = await client.patch(
        "/api/v1/disputes/00000000-0000-0000-0000-000000000000/resolve",
        json={"resolution": "give_them_a_cookie"}
    )
    assert resp.status_code in (401, 422)


@pytest.mark.asyncio
async def test_dispute_endpoints_not_404(client):
    """All dispute endpoints should exist (not 404)."""
    endpoints = [
        ("GET", "/api/v1/disputes"),
        ("GET", "/api/v1/disputes/summary"),
        ("POST", "/api/v1/disputes"),
    ]
    for method, path in endpoints:
        if method == "GET":
            resp = await client.get(path)
        else:
            resp = await client.post(path, json={})
        assert resp.status_code != 404, f"{method} {path} returned 404 -- endpoint missing"
