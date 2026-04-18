"""messages/ — Messaging API split by concern.

Previously one 704-line messages.py. Now a package.
"""

from fastapi import APIRouter

from . import summary, threads, crud, offers

router = APIRouter(prefix="/api/v1/messages", tags=["messages"])

router.include_router(summary.router)
router.include_router(threads.router)
router.include_router(offers.router)  # /offers/* before /{message_id} in crud
router.include_router(crud.router)
