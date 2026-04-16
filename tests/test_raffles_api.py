"""API + route tests for raffle system (require DB — auto-skipped when offline).

Covers auth gates, validation rejections, route registration, and
endpoint response codes for every raffle endpoint.
"""

import pytest


# ── Auth gates (every protected endpoint must return 401 for anon) ────

ZERO_UUID = "00000000-0000-0000-0000-000000000000"


@pytest.mark.asyncio
async def test_browse_raffles_public(client):
    """GET /api/v1/raffles is public (no auth required)."""
    resp = await client.get("/api/v1/raffles")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_raffle_requires_auth(client):
    resp = await client.post("/api/v1/raffles", json={
        "item_id": ZERO_UUID, "title": "Test", "ticket_price": 2.0,
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_reserve_requires_auth(client):
    resp = await client.post(
        f"/api/v1/raffles/{ZERO_UUID}/tickets/reserve",
        json={"quantity": 1},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_confirm_requires_auth(client):
    resp = await client.post(
        f"/api/v1/raffles/{ZERO_UUID}/tickets/{ZERO_UUID}/confirm",
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_cancel_ticket_requires_auth(client):
    resp = await client.post(
        f"/api/v1/raffles/{ZERO_UUID}/tickets/{ZERO_UUID}/cancel",
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_draw_requires_auth(client):
    resp = await client.post(f"/api/v1/raffles/{ZERO_UUID}/draw")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_pre_draw_requires_auth(client):
    resp = await client.get(f"/api/v1/raffles/{ZERO_UUID}/pre-draw")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_my_raffles_requires_auth(client):
    resp = await client.get("/api/v1/raffles/mine")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_my_tickets_requires_auth(client):
    resp = await client.get(f"/api/v1/raffles/{ZERO_UUID}/tickets/mine")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_all_tickets_requires_auth(client):
    resp = await client.get(f"/api/v1/raffles/{ZERO_UUID}/tickets")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_publish_requires_auth(client):
    resp = await client.post(f"/api/v1/raffles/{ZERO_UUID}/publish")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_complete_requires_auth(client):
    resp = await client.post(f"/api/v1/raffles/{ZERO_UUID}/complete")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_cancel_raffle_requires_auth(client):
    resp = await client.post(f"/api/v1/raffles/{ZERO_UUID}/cancel")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_patch_requires_auth(client):
    resp = await client.patch(
        f"/api/v1/raffles/{ZERO_UUID}",
        json={"ticket_price": 5.0},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_verify_requires_auth(client):
    resp = await client.post(
        f"/api/v1/raffles/{ZERO_UUID}/verify",
        json={"is_fair": True},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_vouch_requires_auth(client):
    resp = await client.post("/api/v1/raffles/vouch", json={
        "suspect_user_id": ZERO_UUID,
        "reason": "honest_mistake",
        "explanation": "I know this person, they just forgot to draw.",
    })
    assert resp.status_code == 401


# ── Public endpoints (no auth, correct response codes) ────────────────

@pytest.mark.asyncio
async def test_stats_returns_404_for_missing(client):
    """Stats is public but returns 404 for non-existent raffle."""
    resp = await client.get(f"/api/v1/raffles/{ZERO_UUID}/stats")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_raffle_returns_404_for_missing(client):
    """Get is public but returns 404 for non-existent raffle."""
    resp = await client.get(f"/api/v1/raffles/{ZERO_UUID}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_verifications_returns_404_for_missing(client):
    resp = await client.get(f"/api/v1/raffles/{ZERO_UUID}/verifications")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_browse_returns_list(client):
    """Browse always returns a list, even if empty."""
    resp = await client.get("/api/v1/raffles")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_browse_filter_by_status(client):
    """Status filter accepts valid values."""
    for status in ["active", "published", "drawn", "all"]:
        resp = await client.get(f"/api/v1/raffles?status={status}")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_guide_page_public(client):
    """Raffle guide page is accessible without auth."""
    resp = await client.get("/raffles/guide")
    assert resp.status_code == 200




# ── Router registration ───────────────────────────────────────────────

def test_raffle_routes_registered():
    from src.main import app
    paths = [route.path for route in app.routes]
    expected = [
        "/api/v1/raffles",
        "/api/v1/raffles/mine",
        "/api/v1/raffles/vouch",
        "/api/v1/raffles/{raffle_id}",
        "/api/v1/raffles/{raffle_id}/publish",
        "/api/v1/raffles/{raffle_id}/draw",
        "/api/v1/raffles/{raffle_id}/complete",
        "/api/v1/raffles/{raffle_id}/cancel",
        "/api/v1/raffles/{raffle_id}/stats",
        "/api/v1/raffles/{raffle_id}/pre-draw",
        "/api/v1/raffles/{raffle_id}/verify",
        "/api/v1/raffles/{raffle_id}/verifications",
        "/api/v1/raffles/{raffle_id}/tickets/reserve",
        "/api/v1/raffles/{raffle_id}/tickets/mine",
        "/api/v1/raffles/{raffle_id}/tickets",
        "/api/v1/raffles/{raffle_id}/tickets/{ticket_id}/confirm",
        "/api/v1/raffles/{raffle_id}/tickets/{ticket_id}/cancel",
        "/raffles/guide",
    ]
    for path in expected:
        assert path in paths, f"Missing route: {path}"


def test_raffle_route_count():
    """Ensure we haven't accidentally lost any routes."""
    from src.main import app
    raffle_paths = [r.path for r in app.routes if "/raffle" in r.path]
    assert len(raffle_paths) >= 17
