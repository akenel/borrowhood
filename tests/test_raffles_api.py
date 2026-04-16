"""API + route tests for raffle system (require DB)."""

import pytest


# ── Auth gate tests ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_browse_raffles_public(client):
    """GET /api/v1/raffles is public (no auth required)."""
    resp = await client.get("/api/v1/raffles")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_raffle_requires_auth(client):
    resp = await client.post("/api/v1/raffles", json={
        "item_id": "00000000-0000-0000-0000-000000000000",
        "title": "Test", "ticket_price": 2.0,
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_reserve_requires_auth(client):
    resp = await client.post("/api/v1/raffles/00000000-0000-0000-0000-000000000000/tickets/reserve",
                             json={"quantity": 1})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_draw_requires_auth(client):
    resp = await client.post("/api/v1/raffles/00000000-0000-0000-0000-000000000000/draw")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_pre_draw_requires_auth(client):
    resp = await client.get("/api/v1/raffles/00000000-0000-0000-0000-000000000000/pre-draw")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_my_raffles_requires_auth(client):
    resp = await client.get("/api/v1/raffles/mine")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_stats_public(client):
    """Stats returns 404 for missing raffle (not 401)."""
    resp = await client.get("/api/v1/raffles/00000000-0000-0000-0000-000000000000/stats")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_verify_requires_auth(client):
    resp = await client.post("/api/v1/raffles/00000000-0000-0000-0000-000000000000/verify",
                             json={"is_fair": True})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_verifications_public(client):
    """Verifications list returns 404 for missing raffle (not 401)."""
    resp = await client.get("/api/v1/raffles/00000000-0000-0000-0000-000000000000/verifications")
    assert resp.status_code == 404


# ── Router registration ───────────────────────────────────────────────

def test_raffle_routes_registered():
    from src.main import app
    paths = [route.path for route in app.routes]
    assert "/api/v1/raffles" in paths
    assert "/api/v1/raffles/mine" in paths
    assert "/api/v1/raffles/{raffle_id}" in paths
    assert "/api/v1/raffles/{raffle_id}/draw" in paths
    assert "/api/v1/raffles/{raffle_id}/tickets/reserve" in paths
    assert "/api/v1/raffles/{raffle_id}/stats" in paths
    assert "/api/v1/raffles/{raffle_id}/verify" in paths
    assert "/api/v1/raffles/{raffle_id}/verifications" in paths
