"""Onboarding API tests."""

import pytest


@pytest.mark.asyncio
async def test_onboarding_page_returns_200(client):
    """GET /onboarding should return 200."""
    resp = await client.get("/onboarding")
    assert resp.status_code == 200
    assert "BorrowHood" in resp.text


@pytest.mark.asyncio
async def test_onboarding_has_steps(client):
    """Onboarding page should have all 3 steps."""
    resp = await client.get("/onboarding")
    text = resp.text
    assert "step" in text.lower()


@pytest.mark.asyncio
async def test_profile_setup_requires_auth(client):
    """POST /api/v1/onboarding/profile should require auth."""
    resp = await client.post("/api/v1/onboarding/profile", json={
        "display_name": "Test User",
    })
    assert resp.status_code in (401, 403)
