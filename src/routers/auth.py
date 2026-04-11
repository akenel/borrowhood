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
    """Redirect to Keycloak login page. If already logged in, go to dashboard."""
    # If user already has a valid session, don't send them to KC again
    from src.dependencies import get_current_user_token
    token = await get_current_user_token(request)
    if token:
        return RedirectResponse(url="/dashboard", status_code=302)
    next_page = request.query_params.get("next", "/")
    # Where to come back after login -- pass next page via state param
    callback_uri = f"{settings.app_url}/auth/callback"
    redirect_uri = quote(callback_uri, safe="")
    state = quote(next_page, safe="")
    login_url = (
        f"{_kc_base()}/auth"
        f"?client_id={settings.kc_client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope=openid+email+profile"
        f"&state={state}"
    )
    return RedirectResponse(url=login_url, status_code=302)


@router.get("/auth/callback")
async def auth_callback(request: Request, code: str = "", state: str = "/"):
    """Exchange authorization code for tokens, set session cookie."""
    if not code:
        return RedirectResponse(url="/", status_code=302)
    next_page = state if state.startswith("/") else "/"

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

    # Set session cookie and redirect to the page user was trying to access
    response = RedirectResponse(url=next_page, status_code=302)
    response.set_cookie(
        "bh_session",
        access_token,
        max_age=token_data.get("expires_in", 1800),
        httponly=True,
        samesite="lax",
        secure=not settings.debug,
    )

    # Process referral cookie (if present)
    ref_slug = request.cookies.get("bh_ref")
    if ref_slug:
        response.delete_cookie("bh_ref")  # One-time use
        try:
            from jose import jwt as _jwt
            decoded = _jwt.decode(access_token, options={"verify_signature": False})
            from sqlalchemy.ext.asyncio import AsyncSession
            from src.database import async_session as async_session_factory
            from src.models.user import BHUser, BHUserPoints
            from sqlalchemy import select
            async with async_session_factory() as db:
                # Find the new user
                kc_id = decoded.get("sub", "")
                result = await db.execute(select(BHUser).where(BHUser.keycloak_id == kc_id))
                new_user = result.scalars().first()
                if new_user and not new_user.referred_by:
                    # Find referrer
                    ref_result = await db.execute(select(BHUser).where(BHUser.slug == ref_slug))
                    referrer = ref_result.scalars().first()
                    if referrer and referrer.id != new_user.id:
                        new_user.referred_by = ref_slug
                        # Award points: 10 to new user, 20 to referrer
                        new_pts = await db.execute(select(BHUserPoints).where(BHUserPoints.user_id == new_user.id))
                        new_pts_obj = new_pts.scalars().first()
                        if new_pts_obj:
                            new_pts_obj.total_points += 10
                        ref_pts = await db.execute(select(BHUserPoints).where(BHUserPoints.user_id == referrer.id))
                        ref_pts_obj = ref_pts.scalars().first()
                        if ref_pts_obj:
                            ref_pts_obj.total_points += 20
                        await db.commit()
                        logger.info("Referral: %s referred %s (slug=%s)", ref_slug, new_user.display_name, new_user.slug)
        except Exception as e:
            logger.warning("Referral processing failed: %s", e)

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


@router.get("/join")
async def join_referral(request: Request):
    """Referral link: /join?ref=akenel -- sets cookie and redirects to signup."""
    ref = request.query_params.get("ref", "").strip()
    # Redirect to Keycloak registration page
    register_url = (
        f"{_kc_base()}/registrations"
        f"?client_id={settings.kc_client_id}"
        f"&redirect_uri={quote(settings.app_url + '/auth/callback', safe='')}"
        f"&response_type=code"
        f"&scope=openid+email+profile"
    )
    response = RedirectResponse(url=register_url, status_code=302)
    if ref:
        response.set_cookie(
            "bh_ref", ref, max_age=30 * 24 * 3600,  # 30 days
            httponly=True, samesite="lax",
        )
    return response
