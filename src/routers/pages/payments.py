"""Payment flow pages: success, cancel."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.config import settings
from src.database import get_db
from src.dependencies import get_current_user_token, get_user
from src.i18n import detect_language, get_translator, SUPPORTED_LANGUAGES
from src.models.item import ATTRIBUTE_SCHEMAS, BHItem, CATEGORY_GROUPS
from src.models.listing import BHListing, ListingStatus, ListingType
from src.models.rental import BHRental, RentalStatus
from src.models.review import BHReview
from src.models.badge import BADGE_INFO
from src.models.user import BadgeTier, BHUser, WorkshopType

from ._helpers import (
    templates, _ctx, _render, _abs_url, _og_workshop_desc,
    _og_item_desc, _last_seen,
)

router = APIRouter(tags=["pages"])

@router.get("/payments/success", response_class=HTMLResponse)
async def payment_success(
    request: Request,
    token: Optional[str] = None,
    PayerID: Optional[str] = None,
):
    """PayPal return page after buyer approves. Auto-captures via JS."""
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html><head><title>Payment Processing - La Piazza</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; background: #f9fafb; }}
        .card {{ background: white; border-radius: 12px; padding: 32px; max-width: 400px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .spinner {{ width: 40px; height: 40px; border: 3px solid #e5e7eb; border-top-color: #6366f1; border-radius: 50%; animation: spin 0.8s linear infinite; margin: 0 auto 16px; }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        .success {{ color: #059669; font-size: 48px; }}
        .error {{ color: #dc2626; }}
        h2 {{ margin: 8px 0; color: #111827; }}
        p {{ color: #6b7280; font-size: 14px; }}
        a {{ color: #6366f1; text-decoration: none; font-weight: 600; }}
    </style></head>
    <body>
    <div class="card" id="status">
        <div class="spinner"></div>
        <h2>Processing Payment...</h2>
        <p>Please wait while we confirm your payment.</p>
    </div>
    <script>
    (async function() {{
        // Read payment info from sessionStorage (set before redirect)
        var paymentId = sessionStorage.getItem('pp_payment_id');
        var orderId = sessionStorage.getItem('pp_order_id');
        var el = document.getElementById('status');

        if (!paymentId || !orderId) {{
            el.innerHTML = '<div class="success">&#10003;</div><h2>Payment Complete</h2><p>Your payment has been processed.</p><p><a href="/orders">Go to Orders</a></p>';
            return;
        }}

        try {{
            var resp = await fetch('/api/v1/payments/capture', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{ payment_id: paymentId, paypal_order_id: orderId }})
            }});
            if (resp.ok) {{
                sessionStorage.removeItem('pp_payment_id');
                sessionStorage.removeItem('pp_order_id');
                el.innerHTML = '<div class="success">&#10003;</div><h2>Payment Successful!</h2><p>The seller has been notified.</p><p><a href="/orders">Go to Orders</a></p>';
            }} else {{
                var err = await resp.json();
                throw new Error(err.detail || 'Capture failed');
            }}
        }} catch(e) {{
            el.innerHTML = '<div class="error">&#10007;</div><h2>Payment Issue</h2><p>' + e.message + '</p><p><a href="/orders">Back to Orders</a></p>';
        }}
    }})();
    </script>
    </body></html>
    """)




async def payment_cancel(request: Request):
    """PayPal return page when buyer cancels."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html><head><title>Payment Cancelled - La Piazza</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; background: #f9fafb; }
        .card { background: white; border-radius: 12px; padding: 32px; max-width: 400px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        h2 { margin: 8px 0; color: #111827; }
        p { color: #6b7280; font-size: 14px; }
        a { display: inline-block; margin-top: 16px; padding: 10px 24px; background: #6366f1; color: white; border-radius: 8px; text-decoration: none; font-weight: 600; }
    </style></head>
    <body>
    <div class="card">
        <div style="font-size: 48px; color: #9ca3af;">&#8617;</div>
        <h2>Payment Cancelled</h2>
        <p>No charge was made. You can try again from your orders page.</p>
        <a href="/orders">Back to Orders</a>
    </div>
    </body></html>
    """)



