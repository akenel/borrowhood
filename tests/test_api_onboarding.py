"""Onboarding API tests."""

import pytest


@pytest.mark.asyncio
async def test_onboarding_redirects_anon(client):
    """Onboarding redirects unauthenticated users to /login."""
    resp = await client.get("/onboarding", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers.get("location", "")


@pytest.mark.asyncio
async def test_profile_setup_requires_auth(client):
    """POST /api/v1/onboarding/profile should require auth."""
    resp = await client.post("/api/v1/onboarding/profile", json={
        "display_name": "Test User",
    })
    assert resp.status_code in (401, 403)
