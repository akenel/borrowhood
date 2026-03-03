"""Stripe Checkout integration service.

Mirrors the PayPal service pattern:
- Create Checkout Session -> redirect buyer to Stripe
- Retrieve session status after completion
- Refund a payment intent

Stripe flow:
1. Server creates Checkout Session -> gets checkout URL
2. Buyer redirects to Stripe, pays
3. Stripe redirects back with session ID
4. Server retrieves session to confirm payment

Docs: https://docs.stripe.com/api/checkout/sessions
"""

import logging
from typing import Optional

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

STRIPE_API_BASE = "https://api.stripe.com/v1"


def _headers() -> dict:
    """Stripe API auth headers (Bearer token)."""
    return {
        "Authorization": f"Bearer {settings.stripe_secret_key}",
    }


async def create_checkout_session(
    amount: float,
    currency: str = "EUR",
    description: str = "BorrowHood Payment",
    success_url: str = "",
    cancel_url: str = "",
) -> Optional[dict]:
    """Create a Stripe Checkout Session.

    Returns dict with 'id' (session ID) and 'url' (redirect buyer here).
    Amount is in major currency units (e.g., 10.50 EUR) -- converted to cents for Stripe.
    """
    if not settings.stripe_secret_key:
        logger.warning("Stripe secret key not configured")
        return None

    amount_cents = int(round(amount * 100))

    form_data = {
        "mode": "payment",
        "line_items[0][price_data][currency]": currency.lower(),
        "line_items[0][price_data][product_data][name]": description,
        "line_items[0][price_data][unit_amount]": str(amount_cents),
        "line_items[0][quantity]": "1",
        "success_url": success_url or f"{settings.app_url}/payments/success?session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": cancel_url or f"{settings.app_url}/payments/cancel",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{STRIPE_API_BASE}/checkout/sessions",
            data=form_data,
            headers=_headers(),
        )

    if resp.status_code in (200, 201):
        data = resp.json()
        return {
            "id": data["id"],
            "url": data.get("url", ""),
            "payment_intent": data.get("payment_intent", ""),
            "status": data.get("status", ""),
        }

    logger.error("Stripe create session failed: %s %s", resp.status_code, resp.text)
    return None


async def retrieve_session(session_id: str) -> Optional[dict]:
    """Retrieve a Checkout Session to check payment status.

    Returns dict with session details including payment_intent and payment_status.
    """
    if not settings.stripe_secret_key:
        return None

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{STRIPE_API_BASE}/checkout/sessions/{session_id}",
            headers=_headers(),
        )

    if resp.status_code == 200:
        data = resp.json()
        return {
            "id": data["id"],
            "payment_intent": data.get("payment_intent", ""),
            "payment_status": data.get("payment_status", ""),
            "status": data.get("status", ""),
            "amount_total": data.get("amount_total", 0),
            "currency": data.get("currency", ""),
        }

    logger.error("Stripe retrieve session failed: %s %s", resp.status_code, resp.text)
    return None


async def refund_payment(
    payment_intent_id: str,
    amount: Optional[float] = None,
    currency: str = "EUR",
) -> Optional[dict]:
    """Refund a payment intent (full or partial).

    If amount is None, issues a full refund.
    """
    if not settings.stripe_secret_key:
        return None

    form_data = {"payment_intent": payment_intent_id}
    if amount is not None:
        form_data["amount"] = str(int(round(amount * 100)))

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{STRIPE_API_BASE}/refunds",
            data=form_data,
            headers=_headers(),
        )

    if resp.status_code in (200, 201):
        data = resp.json()
        return {
            "refund_id": data["id"],
            "status": data.get("status", ""),
            "amount": data.get("amount", 0) / 100,
        }

    logger.error("Stripe refund failed: %s %s", resp.status_code, resp.text)
    return None
