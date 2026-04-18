"""Tests for April 12 BL features: pricing, analytics, mentorship, delivery, saved search.

Covers BL-011, BL-062, BL-073, BL-081, BL-085.
"""

import json
from pathlib import Path

import pytest


RENTALS_PY = Path("src/routers/rentals.py")
LISTINGS_PY = Path("src/routers/listings.py")
MENTORSHIPS_PY = Path("src/routers/mentorships.py")
ANALYTICS_PY = Path("src/routers/analytics.py")
ANALYTICS_MODEL = Path("src/models/analytics.py")
PRICING_PY = Path("src/services/pricing.py")
# PAGES_PY: read the whole pages/ package as one string (after split refactor).
class _PagesContent:
    def read_text(self):
        import os
        root = "src/routers/pages"
        out = []
        for name in sorted(os.listdir(root)):
            if name.endswith(".py"):
                with open(os.path.join(root, name)) as f:
                    out.append(f.read())
        return "\n".join(out)
PAGES_PY = _PagesContent()
DASHBOARD_HTML = Path("src/templates/pages/dashboard.html")
ITEM_DETAIL_HTML = Path("src/templates/pages/item_detail.html")
DELIVERY_HTML = Path("src/templates/pages/delivery_tracking.html")
MAIN_PY = Path("src/main.py")
EN_JSON = Path("src/locales/en.json")
IT_JSON = Path("src/locales/it.json")


# ── BL-011: Team Pricing ──

class TestPricingService:
    def test_pricing_module_exists(self):
        assert PRICING_PY.exists()

    def test_calculate_function(self):
        content = PRICING_PY.read_text()
        assert "def calculate_service_price" in content

    def test_handles_group_discount(self):
        content = PRICING_PY.read_text()
        assert "group_discount_pct" in content

    def test_enforces_minimum_charge(self):
        content = PRICING_PY.read_text()
        assert "minimum_charge" in content
        assert "max(" in content

    def test_validates_max_participants(self):
        content = PRICING_PY.read_text()
        assert "max_participants" in content
        assert "ValueError" in content

    def test_returns_breakdown(self):
        content = PRICING_PY.read_text()
        for key in ["subtotal", "discount", "total", "per_person"]:
            assert f'"{key}"' in content


class TestPricingAPI:
    def test_price_endpoint_exists(self):
        content = LISTINGS_PY.read_text()
        assert "def calculate_price" in content
        assert "/price" in content

    def test_accepts_participants_param(self):
        content = LISTINGS_PY.read_text()
        assert "participants" in content


class TestPricingUI:
    def test_participant_input_in_form(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "rentalForm.participants" in content
        assert "booking.participants" in content

    def test_live_price_calculation(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "calcTeamPrice()" in content
        assert "calcPrice" in content

    def test_group_discount_display(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "booking.group_discount" in content

    def test_total_display(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "booking.total" in content

    def test_participant_count_in_payload(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "participant_count" in content


class TestPricingSchema:
    def test_participant_count_in_rental_create(self):
        content = Path("src/schemas/rental.py").read_text()
        assert "participant_count" in content


# ── BL-085: Seller Analytics ──

class TestAnalyticsModel:
    def test_model_exists(self):
        assert ANALYTICS_MODEL.exists()

    def test_item_view_table(self):
        content = ANALYTICS_MODEL.read_text()
        assert "bh_item_view" in content
        assert "item_id" in content
        assert "viewer_id" in content


class TestAnalyticsAPI:
    def test_router_exists(self):
        assert ANALYTICS_PY.exists()

    def test_seller_stats_endpoint(self):
        content = ANALYTICS_PY.read_text()
        assert "def seller_stats" in content

    def test_returns_per_item_data(self):
        content = ANALYTICS_PY.read_text()
        for key in ["views", "orders", "revenue", "conversion"]:
            assert f'"{key}"' in content

    def test_returns_summary(self):
        content = ANALYTICS_PY.read_text()
        assert '"summary"' in content
        assert "total_views" in content


class TestAnalyticsViewTracking:
    def test_view_tracked_in_item_detail(self):
        content = PAGES_PY.read_text()
        assert "BHItemView" in content

    def test_owner_views_not_tracked(self):
        content = PAGES_PY.read_text()
        assert "not is_owner" in content


class TestAnalyticsDashboard:
    def test_analytics_tab_in_dropdown(self):
        content = DASHBOARD_HTML.read_text()
        assert "value=\"analytics\"" in content

    def test_analytics_tab_content(self):
        content = DASHBOARD_HTML.read_text()
        assert "tab === 'analytics'" in content
        assert "/api/v1/analytics/seller-stats" in content

    def test_summary_cards(self):
        content = DASHBOARD_HTML.read_text()
        assert "dashboard.total_views" in content
        assert "dashboard.total_orders" in content
        assert "dashboard.total_revenue" in content
        assert "dashboard.conversion_rate" in content

    def test_per_item_table(self):
        content = DASHBOARD_HTML.read_text()
        assert "dashboard.item_performance" in content


class TestAnalyticsRegistered:
    def test_registered_in_main(self):
        content = MAIN_PY.read_text()
        assert "analytics" in content


# ── BL-062: Mentorship API ──

class TestMentorshipRouter:
    def test_router_exists(self):
        assert MENTORSHIPS_PY.exists()

    def test_list_endpoint(self):
        content = MENTORSHIPS_PY.read_text()
        assert "def list_mentorships" in content

    def test_create_endpoint(self):
        content = MENTORSHIPS_PY.read_text()
        assert "def create_mentorship" in content

    def test_status_endpoint(self):
        content = MENTORSHIPS_PY.read_text()
        assert "def update_mentorship_status" in content

    def test_progress_endpoint(self):
        content = MENTORSHIPS_PY.read_text()
        assert "def log_progress" in content

    def test_prevents_self_mentorship(self):
        content = MENTORSHIPS_PY.read_text()
        assert "Cannot mentor yourself" in content


class TestMentorshipDashboard:
    def test_mentorships_tab_in_dropdown(self):
        content = DASHBOARD_HTML.read_text()
        assert "value=\"mentorships\"" in content

    def test_mentorships_tab_content(self):
        content = DASHBOARD_HTML.read_text()
        assert "tab === 'mentorships'" in content
        assert "/api/v1/mentorships" in content

    def test_log_progress_form(self):
        content = DASHBOARD_HTML.read_text()
        assert "saveProgress()" in content
        assert "logHours" in content
        assert "logMilestones" in content

    def test_status_actions(self):
        content = DASHBOARD_HTML.read_text()
        assert "updateStatus(m.id, 'active')" in content
        assert "updateStatus(m.id, 'completed')" in content


class TestMentorshipRegistered:
    def test_registered_in_main(self):
        content = MAIN_PY.read_text()
        assert "mentorships" in content


# ── BL-073: Delivery Tracking ──

class TestDeliveryTrackingPage:
    def test_template_exists(self):
        assert DELIVERY_HTML.exists()

    def test_extends_base(self):
        content = DELIVERY_HTML.read_text()
        assert '{% extends "base.html" %}' in content

    def test_leaflet_map(self):
        content = DELIVERY_HTML.read_text()
        assert "delivery-map" in content
        assert "L.map" in content
        assert "L.marker" in content

    def test_event_timeline(self):
        content = DELIVERY_HTML.read_text()
        assert "ev.title" in content
        assert "ev.description" in content

    def test_status_banner(self):
        content = DELIVERY_HTML.read_text()
        assert "tracking.status" in content
        assert "DELIVERED" in content
        assert "IN_TRANSIT" in content

    def test_gps_polyline(self):
        content = DELIVERY_HTML.read_text()
        assert "L.polyline" in content
        assert "event_lat" in content

    def test_route_exists(self):
        content = PAGES_PY.read_text()
        assert "def delivery_tracking_page" in content
        assert "/delivery/" in content


# ── BL-081: Saved Searches Dashboard ──

class TestSavedSearchesDashboard:
    def test_tab_in_dropdown(self):
        content = DASHBOARD_HTML.read_text()
        assert "value=\"saved_searches\"" in content

    def test_tab_content(self):
        content = DASHBOARD_HTML.read_text()
        assert "tab === 'saved_searches'" in content
        assert "/api/v1/saved-searches" in content

    def test_toggle_notifications(self):
        content = DASHBOARD_HTML.read_text()
        assert "toggle(s.id)" in content
        assert "/toggle" in content

    def test_delete_search(self):
        content = DASHBOARD_HTML.read_text()
        assert "remove(s.id)" in content

    def test_match_count_badge(self):
        content = DASHBOARD_HTML.read_text()
        assert "match_count" in content

    def test_empty_state(self):
        content = DASHBOARD_HTML.read_text()
        assert "dashboard.no_saved_searches" in content


# ── Locale Consistency ──

class TestBLLocaleKeys:
    @pytest.fixture
    def en(self):
        return json.loads(EN_JSON.read_text())

    @pytest.fixture
    def it(self):
        return json.loads(IT_JSON.read_text())

    def test_booking_keys(self, en, it):
        for key in ["participants", "group_discount", "total"]:
            assert key in en["booking"], f"Missing en booking.{key}"
            assert key in it["booking"], f"Missing it booking.{key}"

    def test_dashboard_analytics_keys(self, en, it):
        for key in ["analytics", "total_views", "total_orders", "total_revenue", "conversion_rate", "item_performance"]:
            assert key in en["dashboard"], f"Missing en dashboard.{key}"
            assert key in it["dashboard"], f"Missing it dashboard.{key}"

    def test_dashboard_mentorship_keys(self, en, it):
        for key in ["mentorships", "no_mentorships", "hours", "milestones", "notes", "save", "cancel"]:
            assert key in en["dashboard"], f"Missing en dashboard.{key}"
            assert key in it["dashboard"], f"Missing it dashboard.{key}"

    def test_dashboard_saved_search_keys(self, en, it):
        for key in ["saved_searches", "no_saved_searches", "browse_and_save"]:
            assert key in en["dashboard"], f"Missing en dashboard.{key}"
            assert key in it["dashboard"], f"Missing it dashboard.{key}"

    def test_delivery_tracking_keys(self, en, it):
        for key in ["tracking_title", "loading", "destination", "map", "timeline", "no_events"]:
            assert key in en["delivery_tracking"], f"Missing en delivery_tracking.{key}"
            assert key in it["delivery_tracking"], f"Missing it delivery_tracking.{key}"
