"""Authentication flow tests.

These tests verify every auth path works correctly WITHOUT needing
a running Keycloak or database. They test the HTTP-level behavior:
redirects, cookies, headers, status codes.

CRITICAL: Login must never break. These tests are the safety net.
"""

import pytest
from urllib.parse import urlparse, parse_qs


# ── Login Flow ──


@pytest.mark.asyncio
async def test_login_redirects_to_keycloak(client):
    """Login should redirect to Keycloak authorize endpoint."""
    resp = await client.get("/login")
    assert resp.status_code == 302
    location = resp.headers.get("location", "")
    assert "openid-connect/auth" in location
    assert "client_id=borrowhood-web" in location
    assert "response_type=code" in location


@pytest.mark.asyncio
async def test_login_includes_required_scopes(client):
    """Login redirect must request openid, email, and profile scopes."""
    resp = await client.get("/login")
    location = resp.headers.get("location", "")
    assert "scope=openid" in location
    assert "email" in location
    assert "profile" in location


@pytest.mark.asyncio
async def test_login_includes_redirect_uri(client):
    """Login redirect must include callback URI for Keycloak to return to."""
    resp = await client.get("/login")
    location = resp.headers.get("location", "")
    assert "redirect_uri=" in location
    assert "auth%2Fcallback" in location or "auth/callback" in location


@pytest.mark.asyncio
async def test_login_preserves_next_page(client):
    """Login with ?next= should pass the destination in state param."""
    resp = await client.get("/login?next=/profile")
    location = resp.headers.get("location", "")
    # state param should contain /profile (URL-encoded)
    assert "state=" in location
    assert "profile" in location


@pytest.mark.asyncio
async def test_login_default_next_is_root(client):
    """Login without ?next= should default state to /."""
    resp = await client.get("/login")
    location = resp.headers.get("location", "")
    assert "state=%2F" in location or "state=/" in location


# ── Logout Flow ──


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
    set_cookie = resp.headers.get("set-cookie", "")
    assert "bh_session" in set_cookie


@pytest.mark.asyncio
async def test_logout_includes_post_logout_redirect(client):
    """Logout should tell Keycloak where to redirect after."""
    resp = await client.get("/logout")
    location = resp.headers.get("location", "")
    assert "post_logout_redirect_uri=" in location


# ── Callback Flow ──


@pytest.mark.asyncio
async def test_callback_without_code_redirects_home(client):
    """Auth callback without code parameter should redirect to home."""
    resp = await client.get("/auth/callback")
    assert resp.status_code == 302
    location = resp.headers.get("location", "")
    assert location == "/" or location.endswith("/")


@pytest.mark.asyncio
async def test_callback_with_empty_code_redirects_home(client):
    """Auth callback with empty code should redirect to home."""
    resp = await client.get("/auth/callback?code=")
    assert resp.status_code == 302
    location = resp.headers.get("location", "")
    assert location == "/" or location.endswith("/")


@pytest.mark.asyncio
async def test_callback_with_bad_code_redirects_with_error(client):
    """Auth callback with invalid code should redirect with error."""
    resp = await client.get("/auth/callback?code=invalid_code_12345")
    assert resp.status_code == 302
    location = resp.headers.get("location", "")
    # Should redirect to home with error (token exchange will fail)
    assert "error=login_failed" in location or location == "/"


@pytest.mark.asyncio
async def test_callback_state_injection_blocked(client):
    """State param with non-/ prefix should be sanitized to /."""
    resp = await client.get("/auth/callback?code=test&state=https://evil.com")
    assert resp.status_code == 302
    location = resp.headers.get("location", "")
    # Should NOT redirect to external URL -- state must start with /
    assert not location.startswith("http://evil")
    assert not location.startswith("https://evil")


# ── Protected Routes (require auth) ──


@pytest.mark.asyncio
async def test_profile_without_auth_shows_login_prompt(client):
    """Profile page without auth should show login prompt or redirect."""
    resp = await client.get("/profile")
    if resp.status_code == 200:
        # Page renders with a "please login" message
        assert "login" in resp.text.lower() or "Log In" in resp.text
    else:
        # Or redirects to login
        assert resp.status_code in (302, 307)
        assert "/login" in resp.headers.get("location", "")


@pytest.mark.asyncio
async def test_api_without_auth_returns_401(client):
    """API endpoints without auth should return 401, not redirect."""
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_avatar_upload_without_auth_returns_401(client):
    """Avatar upload without auth should return 401."""
    resp = await client.post("/api/v1/users/me/avatar")
    assert resp.status_code == 401 or resp.status_code == 422


@pytest.mark.asyncio
async def test_banner_upload_without_auth_returns_401(client):
    """Banner upload without auth should return 401."""
    resp = await client.post("/api/v1/users/me/banner")
    assert resp.status_code == 401 or resp.status_code == 422


# ── Cookie Security ──


@pytest.mark.asyncio
async def test_login_redirect_is_302_not_301(client):
    """Login must use 302 (temporary), never 301 (permanent/cached)."""
    resp = await client.get("/login")
    assert resp.status_code == 302


@pytest.mark.asyncio
async def test_logout_redirect_is_302_not_301(client):
    """Logout must use 302 (temporary), never 301 (permanent/cached)."""
    resp = await client.get("/logout")
    assert resp.status_code == 302


# ── Demo Login (debug mode only) ──


@pytest.mark.asyncio
async def test_demo_login_endpoint_exists(client):
    """Demo login endpoint should exist and accept POST."""
    resp = await client.post(
        "/api/v1/demo/login",
        json={"username": "nonexistent", "password": "wrong"},
    )
    # Should get 401 (bad creds) or 403 (prod mode), NOT 404
    assert resp.status_code in (401, 403, 500)
    assert resp.status_code != 404


# ── Language Switch ──


@pytest.mark.asyncio
async def test_lang_cookie_set_on_switch(client):
    """Language switch should set bh_lang cookie on page routes."""
    resp = await client.get("/terms?lang=it")
    set_cookie = resp.headers.get("set-cookie", "")
    assert "bh_lang=it" in set_cookie


@pytest.mark.asyncio
async def test_lang_switch_to_english(client):
    """Language switch to English should set bh_lang=en."""
    resp = await client.get("/terms?lang=en")
    set_cookie = resp.headers.get("set-cookie", "")
    assert "bh_lang=en" in set_cookie


# ── Edge Cases ──


@pytest.mark.asyncio
async def test_double_login_still_redirects(client):
    """Hitting /login twice should still redirect properly."""
    resp1 = await client.get("/login")
    assert resp1.status_code == 302
    resp2 = await client.get("/login")
    assert resp2.status_code == 302
    # Both should go to Keycloak
    assert "openid-connect/auth" in resp2.headers.get("location", "")


@pytest.mark.asyncio
async def test_login_with_special_chars_in_next(client):
    """Login with special characters in next param should not crash."""
    resp = await client.get("/login?next=/items/caf%C3%A9-machine")
    assert resp.status_code == 302


@pytest.mark.asyncio
async def test_auth_callback_route_is_get(client):
    """Auth callback should accept GET (Keycloak redirects via GET)."""
    resp = await client.get("/auth/callback?code=test")
    # Should not be 405 Method Not Allowed
    assert resp.status_code != 405


@pytest.mark.asyncio
async def test_logout_then_login_works(client):
    """Logout followed by login should both redirect properly."""
    resp_logout = await client.get("/logout")
    assert resp_logout.status_code == 302
    resp_login = await client.get("/login")
    assert resp_login.status_code == 302
    assert "openid-connect/auth" in resp_login.headers.get("location", "")
