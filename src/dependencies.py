"""FastAPI dependencies for auth, current user, and role checking.

Keycloak JWT verification with auto-provisioning:
- First request with valid JWT creates user in app DB
- Subsequent requests fetch existing user
- Role checking via Keycloak realm roles
"""

import logging
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional
from urllib.parse import quote
from uuid import UUID

import httpx
from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt
from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import get_db
from src.models.user import BHUser, BHUserPoints

logger = logging.getLogger(__name__)


async def get_user(db: AsyncSession, token: dict) -> BHUser:
    """Resolve a Keycloak JWT token to a BHUser record.

    Auto-links seed data users on first login: if no user matches
    keycloak_id (sub), falls back to matching by preferred_username
    (slug) and updates the keycloak_id for future lookups.
    """
    kc_id = token.get("sub", "")
    result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == kc_id)
    )
    user = result.scalars().first()
    if user:
        user.last_active_at = datetime.now(timezone.utc)
        # Sync username from Keycloak if not set or changed
        kc_username = token.get("preferred_username", "")
        if kc_username and user.username != kc_username:
            user.username = kc_username
        await db.commit()
        return user

    # Fallback: match by username/slug (links seed users on first KC login)
    username = token.get("preferred_username", "")
    if username:
        # Try exact slug match first
        result = await db.execute(
            select(BHUser).where(BHUser.slug == username)
        )
        user = result.scalars().first()

        # Try slug prefix match (e.g. KC "mike" -> DB "mikes-garage")
        if not user:
            result = await db.execute(
                select(BHUser).where(BHUser.slug.startswith(username + "s-"))
            )
            user = result.scalars().first()

        if user:
            logger.info("Auto-linking user '%s' (slug=%s) to keycloak_id %s", username, user.slug, kc_id)
            user.keycloak_id = kc_id
            user.username = username
            user.last_active_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(user)
            return user

    # Auto-provision: create BHUser from JWT claims
    email = token.get("email", f"{username}@borrowhood.local")
    display_name = token.get("name") or token.get("preferred_username", "Neighbor")
    base_slug = slugify(username or display_name, max_length=80)

    # Ensure slug uniqueness
    slug = base_slug
    suffix = 1
    while True:
        existing = await db.execute(select(BHUser).where(BHUser.slug == slug))
        if not existing.scalars().first():
            break
        slug = f"{base_slug}-{suffix}"
        suffix += 1

    new_user = BHUser(
        keycloak_id=kc_id,
        username=username or None,
        email=email,
        display_name=display_name,
        slug=slug,
        last_active_at=datetime.now(timezone.utc),
    )
    db.add(new_user)
    await db.flush()

    # Create points record
    new_points = BHUserPoints(user_id=new_user.id, total_points=0)
    db.add(new_points)

    # Award EARLY_ADOPTER badge if before June 2026
    if datetime.now(timezone.utc) < datetime(2026, 6, 1, tzinfo=timezone.utc):
        from src.models.badge import BHBadge, BadgeCode
        early_badge = BHBadge(
            user_id=new_user.id,
            badge_code=BadgeCode.EARLY_ADOPTER,
            reason="Joined during beta",
        )
        db.add(early_badge)

    await db.commit()
    await db.refresh(new_user)
    logger.info("Auto-provisioned user '%s' (slug=%s, id=%s)", display_name, slug, new_user.id)
    return new_user

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

        # HTML page: redirect to /login which handles the OIDC flow properly
        next_url = quote(request.url.path, safe="")
        raise HTTPException(
            status_code=307,
            headers={"Location": f"/login?next={next_url}"},
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


# Badge tier ordering for gating comparisons
_TIER_ORDER = {
    "newcomer": 0,
    "active": 1,
    "trusted": 2,
    "pillar": 3,
    "legend": 4,
}


def require_badge_tier(min_tier: str):
    """Dependency factory: require minimum badge tier.

    Tier hierarchy: NEWCOMER < ACTIVE < TRUSTED < PILLAR < LEGEND
    Usage: Depends(require_badge_tier("active"))
    """
    min_level = _TIER_ORDER.get(min_tier, 0)

    async def check_tier(
        token: dict = Depends(require_auth),
        db: AsyncSession = Depends(get_db),
    ) -> dict:
        user = await get_user(db, token)
        user_level = _TIER_ORDER.get(user.badge_tier.value, 0)
        if user_level < min_level:
            raise HTTPException(
                status_code=403,
                detail=f"Badge tier '{min_tier}' required. You are '{user.badge_tier.value}'. "
                       f"Earn more points to unlock this action.",
            )
        return token

    return check_tier


# ── Per-user action throttle (BL-024/025/026) ─────────────────────────
# In-memory sliding window per (user_id, action).
# Zero dependencies -- no Redis, no DB writes.

import time as _time
from collections import defaultdict as _defaultdict

_user_actions: dict[str, list[float]] = _defaultdict(list)
_user_actions_cleanup = 0.0


def _cleanup_user_actions(now: float, window: int = 3600):
    global _user_actions_cleanup
    if now - _user_actions_cleanup < 300:
        return
    _user_actions_cleanup = now
    cutoff = now - window
    stale = [k for k, v in _user_actions.items() if not v or v[-1] < cutoff]
    for k in stale:
        del _user_actions[k]


def user_throttle(action: str, limit: int, window_seconds: int = 3600):
    """Dependency factory: limit how many times a user can do `action` per window.

    Usage: Depends(user_throttle("send_message", 50, 3600))
    Means: max 50 messages per hour per user.
    """
    async def check_throttle(token: dict = Depends(require_auth)) -> dict:
        user_id = token.get("sub", "anon")
        key = f"{user_id}:{action}"
        now = _time.monotonic()
        _cleanup_user_actions(now)

        cutoff = now - window_seconds
        timestamps = [t for t in _user_actions[key] if t > cutoff]

        if len(timestamps) >= limit:
            raise HTTPException(
                status_code=429,
                detail=f"Too many actions. Limit: {limit} per {window_seconds // 60} minutes.",
            )

        timestamps.append(now)
        _user_actions[key] = timestamps
        return token

    return check_throttle
