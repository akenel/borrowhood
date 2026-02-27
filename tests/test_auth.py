"""Authentication flow tests."""

import pytest


@pytest.mark.asyncio
async def test_login_redirects_to_keycloak(client):
    """Login should redirect to Keycloak authorize endpoint."""
    resp = await client.get("/login")
    assert resp.status_code == 302
    location = resp.headers.get("location", "")
    assert "keycloak" in location.lower() or "borrowhood" in location.lower()
    assert "openid-connect/auth" in location
    assert "client_id=borrowhood-web" in location
    assert "response_type=code" in location


@pytest.mark.asyncio
async def test_logout_redirects_to_keycloak(client):
    """Logout should redirect to Keycloak logout endpoint."""
    resp = await client.get("/logout")
    assert resp.status_code == 302
    location = resp.headers.get("location", "")
    assert "openid-connect/logout" in location
    assert "client_id=borrowhood-web" in location


@pytest.mark.asyncio
async def test_logout_clears_cookie(client):
    """Logout should clear the bh_session cookie."""
    resp = await client.get("/logout")
    # Check set-cookie header clears the session
    set_cookie = resp.headers.get("set-cookie", "")
    assert "bh_session" in set_cookie


@pytest.mark.asyncio
async def test_callback_without_code_redirects_home(client):
    """Auth callback without code parameter should redirect to home."""
    resp = await client.get("/auth/callback")
    assert resp.status_code == 302
    location = resp.headers.get("location", "")
    assert location == "/" or location.endswith("/")


@pytest.mark.asyncio
async def test_unauthenticated_home_shows_login(client):
    """Home page without auth should show Login button, not logout."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "Log In" in resp.text or "login" in resp.text.lower()
    # Should NOT show My Workshop (only visible when logged in)
    assert "My Workshop" not in resp.text


@pytest.mark.asyncio
async def test_nav_shows_language_switch(client):
    """Navigation should show language toggle."""
    resp = await client.get("/")
    # When viewing English, should see IT toggle
    assert "?lang=it" in resp.text or "?lang=en" in resp.text
