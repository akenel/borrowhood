"""Demo login: ROPC auto-login for UAT testing. Debug mode only.

Uses Keycloak Resource Owner Password Credentials grant to log in as
any test user with one click. Sets bh_session cookie and returns JSON.
"""

import logging

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from src.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/demo", tags=["demo"])


class DemoLoginRequest(BaseModel):
    username: str
    password: str = "helix_pass"


@router.post("/login")
async def demo_login(data: DemoLoginRequest):
    """ROPC login: exchange username/password for JWT, set cookie.

    Debug-only endpoint. Returns 403 in production.
    """
    if not settings.debug:
        raise HTTPException(status_code=403, detail="Demo login disabled in production")

    token_url = (
        f"{settings.kc_url}/realms/{settings.kc_realm}"
        f"/protocol/openid-connect/token"
    )

    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.post(
            token_url,
            data={
                "grant_type": "password",
                "client_id": settings.kc_client_id,
                "username": data.username,
                "password": data.password,
            },
        )

    if resp.status_code != 200:
        detail = "Login failed"
        try:
            err = resp.json()
            detail = err.get("error_description", err.get("error", detail))
        except Exception:
            pass
        logger.warning("Demo login failed for %s: %s", data.username, detail)
        raise HTTPException(status_code=401, detail=detail)

    tokens = resp.json()
    access_token = tokens["access_token"]

    response = JSONResponse({"status": "ok", "username": data.username})
    response.set_cookie(
        "bh_session",
        access_token,
        max_age=tokens.get("expires_in", 3600),
        httponly=True,
        samesite="lax",
        secure=False,  # dev mode, no HTTPS required
    )
    return response
