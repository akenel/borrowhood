"""Shared helpers and constants for items/ package."""
from pathlib import Path

from slugify import slugify
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.item import BHItem

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "uploads"
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10 MB
MAX_VIDEO_SIZE = 50 * 1024 * 1024   # 50 MB


async def _unique_slug(db: AsyncSession, base: str) -> str:
    """Generate a unique slug, appending a counter if needed."""
    slug = slugify(base, max_length=200)
    candidate = slug
    counter = 1
    while True:
        exists = await db.scalar(
            select(func.count(BHItem.id)).where(BHItem.slug == candidate)
        )
        if not exists:
            return candidate
        candidate = f"{slug}-{counter}"
        counter += 1
