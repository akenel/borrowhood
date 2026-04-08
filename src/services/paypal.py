"""PayPal integration service.

Uses PayPal REST API v2 for:
- Creating orders (buyer approval flow)
- Capturing payments
- Issuing refunds

PayPal flow:
1. Server creates order -> gets approval URL
2. Buyer redirects to PayPal, approves
3. Buyer returns to our site with order ID
4. Server captures the payment

Sandbox docs: https://developer.paypal.com/docs/api/orders/v2/
"""

import logging
from typing import Optional

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

PAYPAL_URLS = {
    "sandbox": "https://api-m.sandbox.paypal.com",
    "live": "https://api-m.paypal.com",
}


async def _get_access_token() -> Optional[str]:
    """Get PayPal OAuth2 access token."""
    if not settings.paypal_client_id or not settings.paypal_client_secret:
        logger.warning("PayPal credentials not configured")
        return None

    base_url = PAYPAL_URLS.get(settings.paypal_mode, PAYPAL_URLS["sandbox"])

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/v1/oauth2/token",
            auth=(settings.paypal_client_id, settings.paypal_client_secret),
            data={"grant_type": "client_credentials"},
            headers={"Accept": "application/json"},
        )
        if resp.status_code == 200:
            return resp.json().get("access_token")
        logger.error("PayPal auth failed: %s %s", resp.status_code, resp.text)
        return None


async def create_order(
    amount: float,
    currency: str = "EUR",
    description: str = "BorrowHood Payment",
    return_url: str = "",
    cancel_url: str = "",
) -> Optional[dict]:
    """Create a PayPal order for buyer approval.

    Returns dict with 'id' (order ID) and 'approval_url' (redirect buyer here).
    """
    token = await _get_access_token()
    if not token:
        return None

    base_url = PAYPAL_URLS.get(settings.paypal_mode, PAYPAL_URLS["sandbox"])

    order_data = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": currency,
                "value": f"{amount:.2f}",
            },
            "description": description,
        }],
        "payment_source": {
            "paypal": {
                "experience_context": {
                    "return_url": return_url or f"{settings.app_url}/payments/success",
                    "cancel_url": cancel_url or f"{settings.app_url}/payments/cancel",
                    "brand_name": "La Piazza",
                    "user_action": "PAY_NOW",
                }
            }
        }
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/v2/checkout/orders",
            json=order_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

    if resp.status_code in (200, 201):
        data = resp.json()
        approval_url = None
        for link in data.get("links", []):
            if link.get("rel") == "payer-action":
                approval_url = link["href"]
                break
        return {
            "id": data["id"],
            "status": data["status"],
            "approval_url": approval_url,
        }

    logger.error("PayPal create order failed: %s %s", resp.status_code, resp.text)
    return None


async def capture_order(order_id: str) -> Optional[dict]:
    """Capture a PayPal order after buyer approval.

    Returns dict with capture details including 'capture_id'.
    """
    token = await _get_access_token()
    if not token:
        return None

    base_url = PAYPAL_URLS.get(settings.paypal_mode, PAYPAL_URLS["sandbox"])

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/v2/checkout/orders/{order_id}/capture",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

    if resp.status_code in (200, 201):
        data = resp.json()
        capture_id = None
        captures = data.get("purchase_units", [{}])[0].get("payments", {}).get("captures", [])
        if captures:
            capture_id = captures[0].get("id")
        return {
            "order_id": data["id"],
            "status": data["status"],
            "capture_id": capture_id,
        }

    logger.error("PayPal capture failed: %s %s", resp.status_code, resp.text)
    return None


async def refund_capture(capture_id: str, amount: Optional[float] = None, currency: str = "EUR") -> Optional[dict]:
    """Refund a captured payment (full or partial).

    If amount is None, issues a full refund.
    """
    token = await _get_access_token()
    if not token:
        return None

    base_url = PAYPAL_URLS.get(settings.paypal_mode, PAYPAL_URLS["sandbox"])

    refund_data = {}
    if amount is not None:
        refund_data = {
            "amount": {
                "currency_code": currency,
                "value": f"{amount:.2f}",
            }
        }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{base_url}/v2/payments/captures/{capture_id}/refund",
            json=refund_data,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
        )

    if resp.status_code in (200, 201):
        data = resp.json()
        return {
            "refund_id": data["id"],
            "status": data["status"],
        }

    logger.error("PayPal refund failed: %s %s", resp.status_code, resp.text)
    return None
