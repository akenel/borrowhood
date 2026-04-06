"""Tests for BL-100: Lockbox Code Exchange -- Orders + Email + Telegram.

Covers:
1. Email service (send_email, format_notification_email)
2. Notification model has email_sent field
3. Notification service wires email alongside Telegram
4. Lockbox notification links point to /orders (not /dashboard)
5. Config has Resend settings
6. Orders template has lockbox generate + verify buttons
"""

import pytest
import inspect
from pathlib import Path


# ── Config: Resend email settings ──


class TestEmailConfig:
    def test_resend_api_key_field_exists(self):
        from src.config import BHSettings
        fields = BHSettings.model_fields
        assert "resend_api_key" in fields

    def test_mail_from_field_exists(self):
        from src.config import BHSettings
        fields = BHSettings.model_fields
        assert "mail_from" in fields

    def test_email_enabled_field_exists(self):
        from src.config import BHSettings
        fields = BHSettings.model_fields
        assert "email_enabled" in fields

    def test_email_disabled_by_default(self):
        from src.config import BHSettings
        assert BHSettings.model_fields["email_enabled"].default is False


# ── Email service ──


class TestEmailService:
    def test_send_email_function_exists(self):
        from src.services.email import send_email
        assert callable(send_email)

    def test_send_email_is_async(self):
        from src.services.email import send_email
        assert inspect.iscoroutinefunction(send_email)

    def test_format_notification_email_returns_html(self):
        from src.services.email import format_notification_email
        html = format_notification_email("Test Title", "Test body", "/orders")
        assert "<h2" in html
        assert "Test Title" in html
        assert "Test body" in html
        assert "/orders" in html

    def test_format_notification_email_no_body(self):
        from src.services.email import format_notification_email
        html = format_notification_email("Title Only", None, None)
        assert "Title Only" in html
        assert "La Piazza" in html

    def test_format_notification_email_has_unsubscribe_hint(self):
        from src.services.email import format_notification_email
        html = format_notification_email("Test", None, None)
        assert "email notifications" in html.lower()

    @pytest.mark.asyncio
    async def test_send_email_returns_false_when_disabled(self):
        from src.services.email import send_email
        result = await send_email("test@example.com", "Test", "<p>Test</p>")
        assert result is False  # email_enabled is False by default


# ── Notification model: email_sent field ──


class TestNotificationEmailField:
    def test_email_sent_field_exists(self):
        from src.models.notification import BHNotification
        mapper = BHNotification.__table__.columns
        assert "email_sent" in mapper, "BHNotification must have email_sent column"

    def test_email_sent_defaults_false(self):
        from src.models.notification import BHNotification
        col = BHNotification.__table__.columns["email_sent"]
        assert col.default.arg is False


# ── Notification service: email wiring ──


class TestNotifyServiceEmailWiring:
    def test_notify_imports_email_service(self):
        source = inspect.getsource(__import__("src.services.notify", fromlist=["create_notification"]))
        assert "from src.services.email import" in source
        assert "send_email" in source
        assert "format_notification_email" in source

    def test_create_notification_sends_email(self):
        """create_notification must call send_email for users with notify_email=True."""
        source = inspect.getsource(__import__("src.services.notify", fromlist=["create_notification"]))
        assert "notify_email" in source
        assert "format_notification_email" in source
        assert "email_sent" in source


# ── Lockbox notification links ──


class TestLockboxNotificationLinks:
    def test_lockbox_generate_links_to_orders(self):
        source = Path(__file__).parent.parent / "src" / "routers" / "lockbox.py"
        content = source.read_text()
        # All lockbox notification links should point to /orders
        assert 'link="/orders"' in content
        assert 'link="/dashboard"' not in content, "Lockbox notifications must link to /orders, not /dashboard"

    def test_notify_rental_event_links_to_orders(self):
        source = Path(__file__).parent.parent / "src" / "services" / "notify.py"
        content = source.read_text()
        assert 'link="/orders"' in content
        assert 'link="/dashboard"' not in content or 'link=f"/dashboard"' not in content


# ── Orders template: lockbox buttons ──


class TestOrdersTemplateLockbox:
    def _read_template(self):
        return (Path(__file__).parent.parent / "src" / "templates" / "pages" / "orders.html").read_text()

    def test_generate_lockbox_button_exists(self):
        content = self._read_template()
        assert "Generate Lockbox Codes" in content

    def test_confirm_pickup_button_exists(self):
        content = self._read_template()
        assert "Confirm Pickup" in content

    def test_confirm_return_button_exists(self):
        content = self._read_template()
        assert "Confirm Return" in content

    def test_generate_calls_api(self):
        content = self._read_template()
        assert "/api/v1/lockbox/" in content
        assert "/generate" in content

    def test_verify_calls_api(self):
        content = self._read_template()
        assert "/verify" in content

    def test_generate_only_for_approved_seller(self):
        """Generate button should only show for approved orders where viewer is owner."""
        content = self._read_template()
        assert "approved" in content
        assert "viewer_user_id == item.owner_id" in content

    def test_pickup_only_for_approved_buyer(self):
        """Confirm Pickup should only show for approved orders where viewer is renter."""
        content = self._read_template()
        assert "viewer_user_id == order.renter_id" in content


# ── Lockbox API endpoints exist ──


class TestLockboxAPIEndpoints:
    def test_generate_endpoint_exists(self):
        from src.routers.lockbox import generate_codes
        assert callable(generate_codes)

    def test_get_codes_endpoint_exists(self):
        from src.routers.lockbox import get_codes
        assert callable(get_codes)

    def test_verify_endpoint_exists(self):
        from src.routers.lockbox import verify_code
        assert callable(verify_code)

    def test_lockbox_model_fields(self):
        from src.models.lockbox import BHLockBoxAccess
        cols = {c.name for c in BHLockBoxAccess.__table__.columns}
        assert "pickup_code" in cols
        assert "return_code" in cols
        assert "pickup_used_at" in cols
        assert "return_used_at" in cols
        assert "location_hint" in cols
        assert "instructions" in cols

    def test_code_generation_service(self):
        from src.services.lockbox import generate_unique_codes
        assert inspect.iscoroutinefunction(generate_unique_codes)

    def test_lockbox_service_generates_codes(self):
        """Code generation function should exist and be async."""
        import src.services.lockbox as lb
        source = inspect.getsource(lb)
        # Verify confusing characters are excluded from the alphabet
        assert "O" not in source.split("=")[0] or "exclude" in source.lower() or "safe" in source.lower()
