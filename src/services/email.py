"""Email sending service via Resend API.

Best-effort delivery -- logs errors but never crashes the caller.
"""

import logging
from typing import Optional

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


async def send_email(
    to: str,
    subject: str,
    html: str,
    reply_to: Optional[str] = None,
) -> bool:
    """Send an email via Resend. Returns True if accepted, False on failure."""
    if not settings.email_enabled or not settings.resend_api_key:
        logger.debug("Email disabled or no API key -- skipping email to %s", to)
        return False

    payload = {
        "from": settings.mail_from,
        "to": [to],
        "subject": subject,
        "html": html,
    }
    if reply_to:
        payload["reply_to"] = reply_to

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                RESEND_API_URL,
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Content-Type": "application/json",
                },
            )
            if resp.status_code in (200, 201):
                logger.info("Email sent to %s: %s", to, subject)
                return True
            else:
                logger.warning("Resend API error %s: %s", resp.status_code, resp.text)
                return False
    except Exception as e:
        logger.warning("Email send failed for %s: %s", to, e)
        return False


def format_notification_email(title: str, body: Optional[str], link: Optional[str]) -> str:
    """Build a simple HTML email for a notification."""
    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px;">
        <div style="border-bottom: 2px solid #6366f1; padding-bottom: 12px; margin-bottom: 20px;">
            <strong style="font-size: 18px; color: #1f2937;">La Piazza</strong>
        </div>
        <h2 style="font-size: 16px; color: #111827; margin: 0 0 12px 0;">{title}</h2>
    """
    if body:
        html += f'<p style="font-size: 14px; color: #4b5563; line-height: 1.6; margin: 0 0 16px 0;">{body}</p>'
    if link:
        full_link = link if link.startswith("http") else f"{settings.app_url}{link}"
        html += f"""
        <a href="{full_link}"
           style="display: inline-block; padding: 10px 20px; background-color: #6366f1; color: #ffffff;
                  text-decoration: none; border-radius: 6px; font-size: 14px; font-weight: 600;">
            View on La Piazza
        </a>
        """
    html += """
        <p style="font-size: 12px; color: #9ca3af; margin-top: 24px; border-top: 1px solid #e5e7eb; padding-top: 12px;">
            You received this because you have email notifications enabled on La Piazza.
        </p>
    </div>
    """
    return html
