"""Serve the deterministic generative avatar (services/avatar.py).

GET /api/v1/avatar/{seed}.svg -> an image/svg+xml mark unique to `seed`
(username or display name). Deterministic, so it's cached immutable. Templates
use it as the single fallback for users with no photo.
"""
from fastapi import APIRouter, Response

from src.services.avatar import generate_avatar_svg

router = APIRouter(prefix="/api/v1/avatar", tags=["avatar"])


@router.get("/{seed}.svg")
async def avatar_svg(seed: str) -> Response:
    return Response(
        content=generate_avatar_svg(seed),
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=31536000, immutable"},
    )
