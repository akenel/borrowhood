"""helpboard/ — Help Board API split by concern.

Previously one 843-line helpboard.py. Now a package.
"""

from fastapi import APIRouter

from . import posts, upvotes, replies, media, summary_and_crosslinks
# Re-export specific handlers for tests
from .posts import suggested_helpers  # noqa: F401

router = APIRouter(prefix="/api/v1/helpboard", tags=["helpboard"])

router.include_router(posts.router)
router.include_router(upvotes.router)
router.include_router(replies.router)
router.include_router(media.router)
router.include_router(summary_and_crosslinks.router)
