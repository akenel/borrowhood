"""reviews/ — Review API split by concern.

Previously one 484-line reviews.py. Now a package.

list_reviews and create_review are attached directly to the aggregator
(not via include_router) so the public paths stay `/api/v1/reviews`
without a trailing slash — preserving the existing API contract.
"""

from typing import List

from fastapi import APIRouter

from . import crud, owner, photos, reads, votes
from ._shared import _enrich_review  # noqa: F401
from src.schemas.review import ReviewOut

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])

# Zero-path operations attach to the aggregator directly (FastAPI rejects
# include_router when both prefix and path are empty).
router.add_api_route("", reads.list_reviews, methods=["GET"], response_model=List[ReviewOut])
router.add_api_route("", crud.create_review, methods=["POST"], response_model=ReviewOut, status_code=201)

router.include_router(reads.router)
router.include_router(crud.router)
router.include_router(photos.router)
router.include_router(owner.router)
router.include_router(votes.router)
