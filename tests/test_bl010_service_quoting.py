"""Tests for BL-010: Service Quoting Workflow.

Covers:
1. Quote request form on service/training item detail pages
2. Quotes tab on orders page
3. Quote API endpoints exist and have correct signatures
4. Quote model and state machine
5. Notification links point to /orders?tab=quotes
6. i18n keys for quoting
"""

import pytest
import inspect
from pathlib import Path

from src.i18n import get_translator


# ── i18n: Quote-related keys ──


class TestQuoteTranslations:
    KEYS = [
        "i18n.request_a_quote",
        "i18n.what_do_you_need",
        "i18n.quotes",
        "i18n.submit_quote",
        "i18n.accept_quote",
        "i18n.decline_quote",
        "i18n.labor_hours",
        "i18n.total_amount",
        "i18n.no_quotes_yet",
        "i18n.as_customer",
        "i18n.as_provider",
    ]

    @pytest.mark.parametrize("key", KEYS)
    def test_keys_resolve_en(self, key):
        t = get_translator("en")
        assert t(key) != key, f"EN key '{key}' not translated"

    @pytest.mark.parametrize("key", KEYS)
    def test_keys_resolve_it(self, key):
        t = get_translator("it")
        assert t(key) != key, f"IT key '{key}' not translated"


# ── Quote model and state machine ──


class TestQuoteModel:
    def test_model_exists(self):
        from src.models.quote import BHServiceQuote
        cols = {c.name for c in BHServiceQuote.__table__.columns}
        assert "customer_id" in cols
        assert "provider_id" in cols
        assert "listing_id" in cols
        assert "total_amount" in cols
        assert "labor_hours" in cols
        assert "status" in cols

    def test_quote_statuses(self):
        from src.models.quote import QuoteStatus
        values = {e.value for e in QuoteStatus}
        expected = {"requested", "quoted", "accepted", "in_progress", "completed", "declined", "cancelled"}
        assert expected.issubset(values)

    def test_valid_transitions(self):
        from src.models.quote import VALID_QUOTE_TRANSITIONS as VALID_TRANSITIONS, QuoteStatus
        # REQUESTED can go to QUOTED
        assert QuoteStatus.QUOTED in VALID_TRANSITIONS[QuoteStatus.REQUESTED]
        # QUOTED can go to ACCEPTED or DECLINED
        assert QuoteStatus.ACCEPTED in VALID_TRANSITIONS[QuoteStatus.QUOTED]
        assert QuoteStatus.DECLINED in VALID_TRANSITIONS[QuoteStatus.QUOTED]


# ── Quote API endpoints ──


class TestQuoteEndpoints:
    def test_request_quote_exists(self):
        from src.routers.service_quotes import request_quote
        assert inspect.iscoroutinefunction(request_quote)

    def test_list_quotes_exists(self):
        from src.routers.service_quotes import list_quotes
        assert inspect.iscoroutinefunction(list_quotes)

    def test_submit_pricing_endpoint_exists(self):
        """Provider must be able to submit pricing on a quote."""
        from src.routers.service_quotes import submit_quote
        assert inspect.iscoroutinefunction(submit_quote)

    def test_status_update_endpoint_exists(self):
        from src.routers.service_quotes import update_quote_status
        assert inspect.iscoroutinefunction(update_quote_status)

    def test_notification_links_to_quotes_tab(self):
        source = Path(__file__).parent.parent / "src" / "routers" / "service_quotes.py"
        content = source.read_text()
        assert 'link="/orders?tab=quotes"' in content
        assert 'link="/dashboard"' not in content


# ── Item detail: Quote request button ──


class TestItemDetailQuoteButton:
    def _read_template(self):
        return (Path(__file__).parent.parent / "src" / "templates" / "pages" / "item_detail.html").read_text()

    def test_request_quote_button_exists(self):
        content = self._read_template()
        assert "request_a_quote" in content

    def test_quote_form_calls_api(self):
        content = self._read_template()
        assert "/api/v1/service-quotes" in content

    def test_redirects_to_quotes_tab(self):
        content = self._read_template()
        assert "tab=quotes" in content

    def test_service_training_gets_quote_button(self):
        """Service/training listings should get quote button, not rental form."""
        content = self._read_template()
        assert "listing_type_val.val in ('service', 'training')" in content


# ── Orders page: Quotes tab ──


class TestOrdersQuotesTab:
    def _read_template(self):
        return (Path(__file__).parent.parent / "src" / "templates" / "pages" / "orders.html").read_text()

    def test_tab_navigation_exists(self):
        content = self._read_template()
        assert "tab=orders" in content
        assert "tab=quotes" in content

    def test_quotes_tab_shows_quote_cards(self):
        content = self._read_template()
        assert "quote.status.value" in content

    def test_submit_quote_button_for_provider(self):
        content = self._read_template()
        assert "submit_quote" in content
        assert "showQuoteForm" in content

    def test_accept_decline_buttons_for_customer(self):
        content = self._read_template()
        assert "accept_quote" in content
        assert "decline_quote" in content

    def test_start_work_button(self):
        content = self._read_template()
        assert "Start Work" in content

    def test_mark_complete_button(self):
        content = self._read_template()
        assert "Mark Complete" in content


# ── Orders page router: quotes fetch ──


class TestOrdersRouterQuotes:
    def test_orders_page_accepts_tab_param(self):
        source = inspect.getsource(
            __import__("src.routers.pages", fromlist=["orders_page"]).orders_page
        )
        assert "tab" in source
        assert "quotes" in source

    def test_orders_page_fetches_service_quotes(self):
        source = inspect.getsource(
            __import__("src.routers.pages", fromlist=["orders_page"]).orders_page
        )
        assert "BHServiceQuote" in source
        assert "selected_tab" in source


@pytest.mark.asyncio
async def test_orders_quotes_tab_no_crash(client):
    """Orders page with tab=quotes should not crash."""
    resp = await client.get("/orders?tab=quotes")
    assert resp.status_code in (200, 302)


@pytest.mark.asyncio
async def test_orders_quotes_with_filters(client):
    """Quotes tab should accept role and status filters."""
    resp = await client.get("/orders?tab=quotes&role=customer&status=requested")
    assert resp.status_code in (200, 302)
