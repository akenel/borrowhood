"""Tests for April 12, 2026 -- Rental Calendar features.

Covers:
1. Rental calendar API endpoint in rentals.py
2. Listing availability API endpoint
3. My Rentals tab on calendar page
4. Availability calendar on item detail page
5. Locale keys for rental calendar (en + it)
6. Calendar grid shows rentals alongside events
7. Rental card displays (role, status, date range, other party)
8. Alpine safety (no t() in x-text)
"""

import json
from pathlib import Path

import pytest


RENTALS_PY = Path("src/routers/rentals.py")
CALENDAR_HTML = Path("src/templates/pages/calendar.html")
ITEM_DETAIL_HTML = Path("src/templates/pages/item_detail.html")
EN_JSON = Path("src/locales/en.json")
IT_JSON = Path("src/locales/it.json")


# ── 1. Rental calendar API ──

class TestRentalCalendarAPI:
    def test_calendar_endpoint_exists(self):
        content = RENTALS_PY.read_text()
        assert "def rental_calendar" in content

    def test_returns_year_month(self):
        content = RENTALS_PY.read_text()
        func = content[content.find("def rental_calendar"):]
        assert '"year": year' in func
        assert '"month": month' in func

    def test_returns_rentals_list(self):
        content = RENTALS_PY.read_text()
        func = content[content.find("def rental_calendar"):]
        assert '"rentals": items' in func

    def test_includes_role_field(self):
        content = RENTALS_PY.read_text()
        func = content[content.find("def rental_calendar"):]
        assert '"role":' in func
        assert '"owner"' in func
        assert '"renter"' in func

    def test_includes_item_slug(self):
        content = RENTALS_PY.read_text()
        func = content[content.find("def rental_calendar"):]
        assert '"item_slug":' in func

    def test_includes_date_fields(self):
        content = RENTALS_PY.read_text()
        func = content[content.find("def rental_calendar"):]
        assert '"start":' in func
        assert '"end":' in func
        assert '"days":' in func

    def test_includes_other_party(self):
        content = RENTALS_PY.read_text()
        func = content[content.find("def rental_calendar"):]
        assert '"other_party":' in func

    def test_filters_active_statuses_only(self):
        content = RENTALS_PY.read_text()
        assert "ACTIVE_STATUSES" in content
        assert "TERMINAL_STATUSES" in content

    def test_queries_both_renter_and_owner(self):
        content = RENTALS_PY.read_text()
        func = content[content.find("def rental_calendar"):]
        assert "renter_id == user.id" in func
        assert "owner_id=user.id" in func

    def test_requires_auth(self):
        content = RENTALS_PY.read_text()
        func = content[content.find("def rental_calendar"):content.find("def rental_calendar") + 200]
        assert "require_auth" in func


# ── 2. Listing availability API ──

class TestAvailabilityAPI:
    def test_availability_endpoint_exists(self):
        content = RENTALS_PY.read_text()
        assert "def listing_availability" in content

    def test_returns_booked_days(self):
        content = RENTALS_PY.read_text()
        func = content[content.find("def listing_availability"):]
        assert '"booked_days":' in func

    def test_returns_constraints(self):
        content = RENTALS_PY.read_text()
        func = content[content.find("def listing_availability"):]
        assert '"min_days":' in func
        assert '"max_days":' in func
        assert '"available_from":' in func
        assert '"available_to":' in func

    def test_no_auth_required(self):
        content = RENTALS_PY.read_text()
        func_start = content.find("def listing_availability")
        func_sig = content[func_start:func_start + 300]
        assert "require_auth" not in func_sig

    def test_returns_listing_id(self):
        content = RENTALS_PY.read_text()
        func = content[content.find("def listing_availability"):]
        assert '"listing_id":' in func


# ── 3. My Rentals tab ──

class TestMyRentalsTab:
    def test_tab_button_exists(self):
        content = CALENDAR_HTML.read_text()
        assert "tab === 'my_rentals'" in content

    def test_tab_label_in_template(self):
        content = CALENDAR_HTML.read_text()
        assert "calendar.tab_my_rentals" in content

    def test_rentals_data_array(self):
        content = CALENDAR_HTML.read_text()
        assert "rentals: []" in content

    def test_loads_rental_api(self):
        content = CALENDAR_HTML.read_text()
        assert "/api/v1/rentals/calendar" in content

    def test_rental_cards_show_role_badge(self):
        content = CALENDAR_HTML.read_text()
        assert "calendar.lending" in content
        assert "calendar.borrowing" in content

    def test_rental_cards_show_date_range(self):
        content = CALENDAR_HTML.read_text()
        assert "formatDateRange(r.start, r.end)" in content

    def test_rental_cards_show_other_party(self):
        content = CALENDAR_HTML.read_text()
        assert "r.other_party" in content
        assert "calendar.with" in content

    def test_rental_cards_show_status(self):
        content = CALENDAR_HTML.read_text()
        assert "r.status" in content

    def test_empty_state_message(self):
        content = CALENDAR_HTML.read_text()
        assert "calendar.no_rentals" in content

    def test_browse_items_link(self):
        content = CALENDAR_HTML.read_text()
        assert 'href="/browse"' in content
        assert "calendar.browse_items" in content


# ── 4. Availability calendar on item detail ──

class TestAvailabilityCalendar:
    def test_availability_section_exists(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "calendar.availability" in content

    def test_fetches_availability_api(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "/api/v1/rentals/availability/" in content

    def test_shows_booked_days_red(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "avIsBooked(day)" in content
        assert "bg-red-100" in content

    def test_shows_available_days_green(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "bg-emerald-50" in content

    def test_has_month_navigation(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "avPrev()" in content
        assert "avNext()" in content

    def test_shows_legend(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "calendar.available_day" in content
        assert "calendar.booked_day" in content

    def test_shows_min_max_days(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "calendar.min_days" in content
        assert "calendar.max_days" in content

    def test_only_shows_for_rental_listings(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "listing_type.value in ('rent', 'service', 'training')" in content

    def test_seven_column_grid(self):
        content = ITEM_DETAIL_HTML.read_text()
        avail_section = content[content.find("calendar.availability"):content.find("Reviews section")]
        assert "grid-cols-7" in avail_section

    def test_today_highlighted(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert "avIsToday(day)" in content


# ── 5. Locale keys ──

class TestRentalCalendarLocales:
    @pytest.fixture
    def en(self):
        return json.loads(EN_JSON.read_text())

    @pytest.fixture
    def it(self):
        return json.loads(IT_JSON.read_text())

    def test_en_rental_keys(self, en):
        cal = en["calendar"]
        for key in ["tab_my_rentals", "no_rentals", "browse_items",
                     "lending", "borrowing", "with", "availability",
                     "available_day", "booked_day", "min_days", "max_days"]:
            assert key in cal, f"Missing en calendar key: {key}"

    def test_it_rental_keys(self, it):
        cal = it["calendar"]
        for key in ["tab_my_rentals", "no_rentals", "browse_items",
                     "lending", "borrowing", "with", "availability",
                     "available_day", "booked_day", "min_days", "max_days"]:
            assert key in cal, f"Missing it calendar key: {key}"

    def test_en_it_keys_still_match(self, en, it):
        en_keys = set(en["calendar"].keys())
        it_keys = set(it["calendar"].keys())
        assert en_keys == it_keys, f"Mismatch: en-it={en_keys - it_keys}, it-en={it_keys - en_keys}"


# ── 6. Calendar grid shows rentals ──

class TestCalendarGridRentals:
    def test_events_on_day_includes_rentals(self):
        content = CALENDAR_HTML.read_text()
        func = content[content.find("eventsOnDay(day)"):content.find("eventsOnDay(day)") + 300]
        assert "rentals" in func

    def test_rental_dots_different_color(self):
        content = CALENDAR_HTML.read_text()
        assert "bg-emerald-100" in content
        assert "bg-emerald-500" in content

    def test_rental_marked_with_is_rental(self):
        content = CALENDAR_HTML.read_text()
        assert "is_rental: true" in content

    def test_format_date_range_function(self):
        content = CALENDAR_HTML.read_text()
        assert "formatDateRange(start, end)" in content


# ── 7. Alpine safety ──

class TestRentalAlpineSafety:
    def test_no_t_in_xtext_calendar(self):
        content = CALENDAR_HTML.read_text()
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if 'x-text="' in line:
                idx = line.find('x-text="') + 8
                end = line.find('"', idx)
                if end > idx:
                    val = line[idx:end]
                    if "{{ t(" in val:
                        assert False, f"Line {i}: t() in x-text: {val[:80]}"

    def test_rental_role_uses_data_attr(self):
        content = CALENDAR_HTML.read_text()
        assert "data-lbl-owner" in content
        assert "data-lbl-renter" in content
        assert "$el.dataset.lblOwner" in content

    def test_rental_with_uses_data_attr(self):
        content = CALENDAR_HTML.read_text()
        assert "data-lbl-with" in content
        assert "$el.dataset.lblWith" in content


# ── 8. API imports ──

class TestRentalAPIImports:
    def test_imports_calendar_module(self):
        content = RENTALS_PY.read_text()
        assert "import calendar as cal_mod" in content

    def test_imports_bhitem(self):
        content = RENTALS_PY.read_text()
        assert "from src.models.item import BHItem" in content

    def test_imports_get_current_user_token(self):
        content = RENTALS_PY.read_text()
        assert "get_current_user_token" in content
