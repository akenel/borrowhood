"""
Shared HTTP helpers for BorrowHood API access.

All agents use these to talk to the BorrowHood REST API.
Auth via demo login endpoint (session cookie).
"""

import os
import httpx

BH_BASE_URL = os.getenv("BH_BASE_URL", "https://46.62.138.218")
BH_DEMO_USER = os.getenv("BH_DEMO_USER", "angel")

# Shared cookie jar for session persistence across calls
_cookies = httpx.Cookies()
_logged_in = False


def _client() -> httpx.Client:
    """Create httpx client with SSL verification disabled (self-signed cert on Hetzner)."""
    return httpx.Client(
        base_url=BH_BASE_URL,
        cookies=_cookies,
        verify=False,
        timeout=30.0,
        follow_redirects=True,
    )


def ensure_login() -> None:
    """Login via demo endpoint if not already authenticated."""
    global _logged_in
    if _logged_in:
        return
    with _client() as client:
        resp = client.post(
            "/api/v1/demo/login",
            json={"username": BH_DEMO_USER},
        )
        if resp.status_code == 200:
            # Session cookie set automatically via cookie jar
            _cookies.update(resp.cookies)
            _logged_in = True
        else:
            # Try form-based login as fallback
            resp = client.post(
                "/api/v1/demo/login",
                data={"username": BH_DEMO_USER},
            )
            if resp.status_code in (200, 302, 303):
                _cookies.update(resp.cookies)
                _logged_in = True


def bh_get(path: str, params: dict = None) -> dict:
    """GET request to BorrowHood API. Returns JSON response."""
    ensure_login()
    with _client() as client:
        resp = client.get(path, params=params)
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"HTTP {resp.status_code}", "detail": resp.text[:500]}


def bh_post(path: str, json_data: dict = None) -> dict:
    """POST request to BorrowHood API. Returns JSON response."""
    ensure_login()
    with _client() as client:
        resp = client.post(path, json=json_data)
        if resp.status_code in (200, 201):
            return resp.json()
        return {"error": f"HTTP {resp.status_code}", "detail": resp.text[:500]}
