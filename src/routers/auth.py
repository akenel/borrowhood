"""Authentication routes: login, logout, callback.

OIDC Authorization Code flow with Keycloak.
- /login: redirects to Keycloak login page
- /auth/callback: exchanges code for tokens, sets session cookie
- /logout: clears session cookie, redirects to Keycloak logout
"""

import logging
from urllib.parse import quote

import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import RedirectResponse

from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["auth"])


def _kc_base() -> str:
    """Keycloak OIDC endpoint base URL."""
    return f"{settings.kc_url}/realms/{settings.kc_realm}/protocol/openid-connect"


@router.get("/login")
async def login(request: Request):
    """Redirect to Keycloak login page."""
    # Where to come back after login
    redirect_uri = quote(f"{settings.app_url}/auth/callback", safe="")
    login_url = (
        f"{_kc_base()}/auth"
        f"?client_id={settings.kc_client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=openid+email+profile"
    )
    return RedirectResponse(url=login_url, status_code=302)


@router.get("/auth/callback")
async def auth_callback(request: Request, code: str = ""):
    """Exchange authorization code for tokens, set session cookie."""
    if not code:
        return RedirectResponse(url="/", status_code=302)

    redirect_uri = f"{settings.app_url}/auth/callback"

    # Exchange code for tokens
    try:
        async with httpx.AsyncClient(verify=False) as client:
            resp = await client.post(
                f"{_kc_base()}/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.kc_client_id,
                    "code": code,
                    "redirect_uri": redirect_uri,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            resp.raise_for_status()
            token_data = resp.json()
    except httpx.HTTPStatusError as e:
        logger.error("Token exchange failed: %s %s", e.response.status_code, e.response.text)
        return RedirectResponse(url="/?error=login_failed", status_code=302)
    except Exception as e:
        logger.error("Token exchange error: %s", e)
        return RedirectResponse(url="/?error=login_failed", status_code=302)

    access_token = token_data.get("access_token")
    if not access_token:
        logger.error("No access_token in response")
        return RedirectResponse(url="/?error=login_failed", status_code=302)

    # Set session cookie and redirect to home
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        "bh_session",
        access_token,
        max_age=token_data.get("expires_in", 1800),
        httponly=True,
        samesite="lax",
        secure=not settings.debug,
    )
    return response


@router.get("/logout")
async def logout(request: Request):
    """Clear session cookie and redirect to Keycloak logout."""
    # Build Keycloak logout URL
    post_logout_uri = quote(settings.app_url, safe="")
    logout_url = (
        f"{_kc_base()}/logout"
        f"?client_id={settings.kc_client_id}"
        f"&post_logout_redirect_uri={post_logout_uri}"
    )

    response = RedirectResponse(url=logout_url, status_code=302)
    response.delete_cookie("bh_session")
    return response
