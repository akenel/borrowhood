"""pages/ — HTML page routes split by domain.

All sub-modules register routes on their own APIRouter, then
__init__.py aggregates them into a single `router` that main.py
imports and mounts. This preserves the old `from src.routers import pages`
behavior while allowing each domain to live in its own file.
"""

from fastapi import APIRouter

from . import (
    account,
    community,
    discover,
    item,
    payments,
    static_pages,
    user,
)
# Re-export shared helpers for backward compat
from ._helpers import (  # noqa: F401
    templates, _ctx, _render,
    _abs_url, _og_item_desc, _og_workshop_desc, _last_seen,
)
# Re-export specific handlers for backward compat with tests
from .account import dashboard  # noqa: F401
from .discover import members_directory  # noqa: F401

router = APIRouter()

# Order matters only for overlapping path patterns. Here they're all distinct.
router.include_router(discover.router)
router.include_router(item.router)
router.include_router(user.router)
router.include_router(account.router)
router.include_router(community.router)
router.include_router(payments.router)
router.include_router(static_pages.router)
