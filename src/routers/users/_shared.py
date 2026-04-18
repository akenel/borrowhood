"""Shared constants and helpers for user_api/ package."""
from pathlib import Path

from sqlalchemy import case
from src.models.user import BadgeTier, BHUser

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "uploads" / "avatars"
BANNER_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "uploads" / "banners"
ALLOWED_AVATAR_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_BANNER_SIZE = 10 * 1024 * 1024  # 10 MB

# Badge tier sort order: legend first, newcomer last
_BADGE_SORT = case(
    (BHUser.badge_tier == BadgeTier.LEGEND, 0),
    (BHUser.badge_tier == BadgeTier.PILLAR, 1),
    (BHUser.badge_tier == BadgeTier.TRUSTED, 2),
    (BHUser.badge_tier == BadgeTier.ACTIVE, 3),
    else_=4,
)
