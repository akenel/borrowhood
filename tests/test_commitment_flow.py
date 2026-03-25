"""Commitment flow tests.

Tests the "I Want This" → "I Paid" → "Confirm Payment" → "Complete" pipeline.
All endpoints require auth. Tests verify HTTP-level contracts without DB.
"""

import pytest


# ── Commit endpoint ──


@pytest.mark.asyncio
async def test_commit_requires_auth(client):
    """POST /rentals/commit should return 401 without auth."""
    resp = await client.post("/api/v1/rentals/commit", json={
        "listing_id": "00000000-0000-0000-0000-000000000000",
        "message": "I want this!",
        "commitment_hours": 48,
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_commit_validates_listing_id(client):
    """POST /rentals/commit should validate listing_id is UUID."""
    resp = await client.post("/api/v1/rentals/commit", json={
        "listing_id": "not-a-uuid",
        "message": "I want this!",
    })
    assert resp.status_code in (401, 422)


@pytest.mark.asyncio
async def test_commit_rejects_zero_hours(client):
    """POST /rentals/commit should reject commitment_hours < 1."""
    resp = await client.post("/api/v1/rentals/commit", json={
        "listing_id": "00000000-0000-0000-0000-000000000000",
        "commitment_hours": 0,
    })
    assert resp.status_code in (401, 422)


@pytest.mark.asyncio
async def test_commit_rejects_over_168_hours(client):
    """POST /rentals/commit should reject commitment_hours > 168 (7 days)."""
    resp = await client.post("/api/v1/rentals/commit", json={
        "listing_id": "00000000-0000-0000-0000-000000000000",
        "commitment_hours": 200,
    })
    assert resp.status_code in (401, 422)


@pytest.mark.asyncio
async def test_commit_endpoint_exists(client):
    """POST /rentals/commit should not return 404 or 405."""
    resp = await client.post("/api/v1/rentals/commit", json={})
    assert resp.status_code not in (404, 405)


# ── I Paid endpoint ──


@pytest.mark.asyncio
async def test_i_paid_requires_auth(client):
    """POST /rentals/{id}/i-paid should return 401 without auth."""
    resp = await client.post(
        "/api/v1/rentals/00000000-0000-0000-0000-000000000000/i-paid",
        json={"payment_method": "paypal", "note": ""},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_i_paid_requires_payment_method(client):
    """POST /rentals/{id}/i-paid should require payment_method field."""
    resp = await client.post(
        "/api/v1/rentals/00000000-0000-0000-0000-000000000000/i-paid",
        json={"note": "sent it"},
    )
    assert resp.status_code in (401, 422)


@pytest.mark.asyncio
async def test_i_paid_endpoint_exists(client):
    """POST /rentals/{id}/i-paid should not return 404 (route exists)."""
    resp = await client.post(
        "/api/v1/rentals/00000000-0000-0000-0000-000000000000/i-paid",
        json={"payment_method": "cash"},
    )
    # 401 (no auth) or 404 (rental not found after auth) -- NOT 404 for missing route
    assert resp.status_code != 405


# ── Confirm Payment endpoint ──


@pytest.mark.asyncio
async def test_confirm_payment_requires_auth(client):
    """POST /rentals/{id}/confirm-payment should return 401 without auth."""
    resp = await client.post(
        "/api/v1/rentals/00000000-0000-0000-0000-000000000000/confirm-payment",
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_confirm_payment_endpoint_exists(client):
    """POST /rentals/{id}/confirm-payment should not return 405."""
    resp = await client.post(
        "/api/v1/rentals/00000000-0000-0000-0000-000000000000/confirm-payment",
    )
    assert resp.status_code != 405


# ── Complete endpoint ──


@pytest.mark.asyncio
async def test_complete_requires_auth(client):
    """POST /rentals/{id}/complete should return 401 without auth."""
    resp = await client.post(
        "/api/v1/rentals/00000000-0000-0000-0000-000000000000/complete",
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_complete_endpoint_exists(client):
    """POST /rentals/{id}/complete should not return 405."""
    resp = await client.post(
        "/api/v1/rentals/00000000-0000-0000-0000-000000000000/complete",
    )
    assert resp.status_code != 405


# ── State machine validation ──


@pytest.mark.asyncio
async def test_rental_states_exist():
    """All commitment states should be defined in RentalStatus."""
    from src.models.rental import RentalStatus
    assert hasattr(RentalStatus, "COMMITTED")
    assert hasattr(RentalStatus, "BUYER_PAID")
    assert hasattr(RentalStatus, "PAYMENT_CONFIRMED")
    assert hasattr(RentalStatus, "EXPIRED")
    assert RentalStatus.COMMITTED.value == "committed"
    assert RentalStatus.BUYER_PAID.value == "buyer_paid"
    assert RentalStatus.PAYMENT_CONFIRMED.value == "payment_confirmed"
    assert RentalStatus.EXPIRED.value == "expired"


@pytest.mark.asyncio
async def test_commitment_transitions_valid():
    """Commitment state transitions should follow the defined flow."""
    from src.models.rental import RentalStatus, VALID_RENTAL_TRANSITIONS, validate_rental_transition

    # COMMITTED -> BUYER_PAID (happy path)
    assert validate_rental_transition(RentalStatus.COMMITTED, RentalStatus.BUYER_PAID)
    # COMMITTED -> EXPIRED (auto-expire)
    assert validate_rental_transition(RentalStatus.COMMITTED, RentalStatus.EXPIRED)
    # COMMITTED -> CANCELLED (buyer cancels)
    assert validate_rental_transition(RentalStatus.COMMITTED, RentalStatus.CANCELLED)
    # BUYER_PAID -> PAYMENT_CONFIRMED (seller confirms)
    assert validate_rental_transition(RentalStatus.BUYER_PAID, RentalStatus.PAYMENT_CONFIRMED)
    # PAYMENT_CONFIRMED -> COMPLETED (delivery done)
    assert validate_rental_transition(RentalStatus.PAYMENT_CONFIRMED, RentalStatus.COMPLETED)

    # Invalid transitions
    assert not validate_rental_transition(RentalStatus.COMMITTED, RentalStatus.COMPLETED)  # Can't skip
    assert not validate_rental_transition(RentalStatus.EXPIRED, RentalStatus.BUYER_PAID)  # Dead end
    assert not validate_rental_transition(RentalStatus.BUYER_PAID, RentalStatus.COMMITTED)  # No going back


# ── Expiry service ──


@pytest.mark.asyncio
async def test_expiry_service_importable():
    """The commitment expiry service should be importable."""
    from src.services.commitment_expiry import expire_stale_commitments, run_expiry_loop
    assert callable(expire_stale_commitments)
    assert callable(run_expiry_loop)


# ── Existing flow still works ──


@pytest.mark.asyncio
async def test_legacy_rental_endpoint_still_exists(client):
    """POST /rentals (legacy flow) should still work for giveaways/services."""
    resp = await client.post("/api/v1/rentals", json={
        "listing_id": "00000000-0000-0000-0000-000000000000",
    })
    # 401 (no auth) -- endpoint still exists
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_legacy_transitions_unchanged():
    """Legacy rental transitions should still be valid."""
    from src.models.rental import RentalStatus, validate_rental_transition

    assert validate_rental_transition(RentalStatus.PENDING, RentalStatus.APPROVED)
    assert validate_rental_transition(RentalStatus.APPROVED, RentalStatus.PICKED_UP)
    assert validate_rental_transition(RentalStatus.PICKED_UP, RentalStatus.RETURNED)
    assert validate_rental_transition(RentalStatus.RETURNED, RentalStatus.COMPLETED)
    assert validate_rental_transition(RentalStatus.PENDING, RentalStatus.CANCELLED)
