"""items/ — Item API split by concern.

Previously one 697-line items.py. Now a package.

Route registration order matters: attributes must come before crud
because `/attribute-schemas` (1 segment) would otherwise match
`/{item_id}` and fail UUID validation.
"""

from fastapi import APIRouter

from . import attributes, crud, favorites, media, votes, whatsapp
# Re-exports for tests / legacy imports
from ._shared import _unique_slug  # noqa: F401
from .crud import update_item  # noqa: F401

router = APIRouter(prefix="/api/v1/items", tags=["items"])

router.include_router(attributes.router)
router.include_router(favorites.router)  # /me/* before /{item_id}/* in crud
router.include_router(crud.router)
router.include_router(media.router)
router.include_router(whatsapp.router)
router.include_router(votes.router)
