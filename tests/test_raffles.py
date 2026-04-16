"""Tests for raffle system: model, engine, and API endpoints."""

import pytest
from datetime import datetime, timedelta, timezone


# ── Model / enum tests ─────────────────────────────────────────────────

def test_raffle_status_enum():
    from src.models.raffle import RaffleStatus
    assert {s.value for s in RaffleStatus} == {
        "draft", "published", "active", "drawn", "completed", "cancelled"
    }


def test_ticket_status_enum():
    from src.models.raffle import RaffleTicketStatus
    assert {s.value for s in RaffleTicketStatus} == {
        "reserved", "confirmed", "expired", "cancelled"
    }


def test_draw_type_enum():
    from src.models.raffle import RaffleDrawType
    assert {s.value for s in RaffleDrawType} == {"date", "soldout", "manual"}


def test_delivery_enum():
    from src.models.raffle import RaffleDelivery
    assert {s.value for s in RaffleDelivery} == {"pickup", "shipping", "digital"}


def test_listing_type_has_raffle():
    from src.models.listing import ListingType
    assert ListingType.RAFFLE.value == "raffle"


# ── Trust tiers ────────────────────────────────────────────────────────

def test_trust_tier_zero_completions():
    from src.models.raffle import max_raffle_value_for
    assert max_raffle_value_for(0) == 10


def test_trust_tier_scales():
    from src.models.raffle import max_raffle_value_for
    assert max_raffle_value_for(1) == 20
    assert max_raffle_value_for(2) == 40
    assert max_raffle_value_for(3) == 80
    assert max_raffle_value_for(4) == 160
    assert max_raffle_value_for(5) == 320


def test_trust_tier_caps_at_ceiling():
    from src.models.raffle import max_raffle_value_for, RAFFLE_HARD_CEILING_EUR
    assert max_raffle_value_for(100) == RAFFLE_HARD_CEILING_EUR


# ── Provably fair draw ─────────────────────────────────────────────────

def test_draw_deterministic():
    """Same seed + same pool = same winner every time."""
    from src.services.raffle_engine import compute_winner
    seed = "abc123"
    ids = ["t1", "t2", "t3"]
    quantities = [1, 2, 1]

    idx1, hash1 = compute_winner(seed, ids, quantities)
    idx2, hash2 = compute_winner(seed, ids, quantities)
    assert idx1 == idx2
    assert hash1 == hash2


def test_draw_different_seed_different_winner():
    """Different seeds give different proof hashes."""
    from src.services.raffle_engine import compute_winner
    ids = ["t1", "t2", "t3"]
    quantities = [1, 1, 1]
    _, h1 = compute_winner("seed_a", ids, quantities)
    _, h2 = compute_winner("seed_b", ids, quantities)
    assert h1 != h2


def test_draw_respects_quantity():
    """User with 3 tickets appears 3 times in the pool."""
    from src.services.raffle_engine import compute_winner
    ids = ["solo", "triple"]
    quantities = [1, 3]
    # Pool should be [solo, triple, triple, triple] = size 4
    # Run 100 draws with different seeds — triple should win ~75%
    triple_wins = 0
    for i in range(100):
        idx, _ = compute_winner(f"seed{i}", ids, quantities)
        pool = ["solo"] + ["triple"] * 3
        if pool[idx] == "triple":
            triple_wins += 1
    assert triple_wins > 50  # statistically should be ~75, floor at 50


def test_draw_single_ticket():
    """One confirmed ticket = guaranteed winner."""
    from src.services.raffle_engine import compute_winner
    idx, proof = compute_winner("any_seed", ["only_ticket"], [1])
    assert idx == 0
    assert len(proof) == 64  # sha256 hex


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
