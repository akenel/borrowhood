"""events/ — Event/RSVP API split by concern.

Previously one 640-line events.py. Now a package.
"""

from fastapi import APIRouter

from . import calendar, leaderboard, rsvp
from ._shared import _check_achievements  # noqa: F401

router = APIRouter(prefix="/api/v1/events", tags=["events"])

# leaderboard + calendar have /leaderboard, /my-stats, /calendar -- register
# before rsvp's /{listing_id}/* paths to keep route matching predictable.
router.include_router(leaderboard.router)
router.include_router(calendar.router)
router.include_router(rsvp.router)
