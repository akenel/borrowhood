"""payments/ — Payment API split by provider.

Previously one 601-line payments.py. Now a package.
"""

from typing import List

from fastapi import APIRouter

from . import paypal, stripe_checkout, stripe_connect
from ._schemas import PaymentOut

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

# list_payments is registered on the aggregator so the public path stays
# /api/v1/payments (no trailing slash). FastAPI disallows empty prefix + empty
# path on include_router, so we attach it here directly.
router.add_api_route(
    "",
    paypal.list_payments,
    methods=["GET"],
    response_model=List[PaymentOut],
)

router.include_router(paypal.router)
router.include_router(stripe_checkout.router)
router.include_router(stripe_connect.router)
