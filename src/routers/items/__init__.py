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

# BL-121: mobile Chrome fetch() drops POST body on 307 redirect. Register the
# collection endpoints at empty path too so /api/v1/items (no slash) doesn't
# 307-redirect to /api/v1/items/ (with slash). Same pattern used for payments.
from typing import List  # noqa: E402
from src.schemas.item import ItemOut  # noqa: E402

router.add_api_route(
    "", crud.list_items, methods=["GET"],
    response_model=List[ItemOut], include_in_schema=False,
)
router.add_api_route(
    "", crud.create_item, methods=["POST"],
    response_model=ItemOut, status_code=201, include_in_schema=False,
)
