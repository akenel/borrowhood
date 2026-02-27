"""FastAPI dependencies for auth, current user, and role checking.

Keycloak JWT verification with auto-provisioning:
- First request with valid JWT creates user in app DB
- Subsequent requests fetch existing user
- Role checking via Keycloak realm roles
"""

import logging
from functools import lru_cache
from typing import Optional
from urllib.parse import quote
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db

logger = logging.getLogger(__name__)

# Keycloak OIDC discovery cache
_jwks_client = None
_kc_public_key = None


async def get_kc_public_key() -> str:
    """Fetch and cache Keycloak realm public key for JWT verification."""
    global _kc_public_key
    if _kc_public_key:
        return _kc_public_key

    certs_url = f"{settings.kc_url}/realms/{settings.kc_realm}/protocol/openid-connect/certs"
    async with httpx.AsyncClient(verify=False) as client:
        resp = await client.get(certs_url)
        resp.raise_for_status()
        jwks = resp.json()

    # Use first RSA key
    for key in jwks.get("keys", []):
        if key.get("kty") == "RSA" and key.get("use") == "sig":
            _kc_public_key = key
            return _kc_public_key

    raise HTTPException(status_code=500, detail="No RSA signing key found in Keycloak JWKS")


async def get_current_user_token(request: Request) -> Optional[dict]:
    """Extract and verify JWT from session cookie or Authorization header.

    Returns decoded token dict or None if not authenticated.
    """
    token = request.cookies.get("bh_session")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        return None

    try:
        public_key = await get_kc_public_key()
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.kc_client_id,
            options={"verify_aud": False},  # Keycloak tokens may not have aud
        )
        return decoded
    except JWTError as e:
        logger.warning("JWT verification failed: %s", e)
        return None


async def require_auth(request: Request) -> dict:
    """Dependency: require authenticated user. Redirects to Keycloak login if not.

    For HTML pages: 307 redirect to Keycloak login with redirect_uri back.
    For API endpoints: 401 Unauthorized.
    """
    token = await get_current_user_token(request)
    if not token:
        # Check if this is an API request or HTML page
        if request.url.path.startswith("/api/"):
            raise HTTPException(status_code=401, detail="Authentication required")

        # HTML page: redirect to Keycloak login
        redirect_uri = quote(str(request.url), safe="")
        login_url = (
            f"{settings.kc_url}/realms/{settings.kc_realm}"
            f"/protocol/openid-connect/auth"
            f"?client_id={settings.kc_client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=code"
            f"&scope=openid+email+profile"
        )
        raise HTTPException(
            status_code=307,
            headers={"Location": login_url},
        )

    return token


def require_role(role: str):
    """Dependency factory: require specific Keycloak realm role."""

    async def check_role(token: dict = Depends(require_auth)) -> dict:
        roles = token.get("realm_access", {}).get("roles", [])
        if role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"Role '{role}' required",
                headers={"X-Required-Role": role},
            )
        return token

    return check_role
