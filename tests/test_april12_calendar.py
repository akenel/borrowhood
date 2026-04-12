"""Tests for April 12, 2026 -- Community Calendar feature.

Covers:
1. Calendar page route exists in pages.py
2. Calendar template exists and extends base.html
3. Calendar API endpoint exists in events.py
4. Calendar locale keys exist (en + it)
5. Nav link to /calendar in base.html (desktop + mobile)
6. Tab structure (community + my_events)
7. Month navigation (prev/next)
8. RSVP buttons in calendar event cards
9. Calendar grid structure (7-column grid)
10. Event cards show essential info (title, time, venue, price)
11. API imports correct models
12. No t() in Alpine expressions (calendar template)
13. Empty state messages for both tabs
14. Create event CTA link
"""

import json
from pathlib import Path

import pytest


# ── Paths ──

PAGES_PY = Path("src/routers/pages.py")
EVENTS_PY = Path("src/routers/events.py")
CALENDAR_HTML = Path("src/templates/pages/calendar.html")
BASE_HTML = Path("src/templates/base.html")
EN_JSON = Path("src/locales/en.json")
IT_JSON = Path("src/locales/it.json")


# ── 1. Page route ──

class TestCalendarRoute:
    def test_calendar_route_exists(self):
        content = PAGES_PY.read_text()
        assert '/calendar' in content
        assert 'def calendar_page' in content

    def test_calendar_route_renders_template(self):
        content = PAGES_PY.read_text()
        assert 'pages/calendar.html' in content


# ── 2. Template ──

class TestCalendarTemplate:
    def test_template_exists(self):
        assert CALENDAR_HTML.exists()

    def test_extends_base(self):
        content = CALENDAR_HTML.read_text()
        assert '{% extends "base.html" %}' in content

    def test_has_block_content(self):
        content = CALENDAR_HTML.read_text()
        assert '{% block content %}' in content


# ── 3. API endpoint ──

class TestCalendarAPI:
    def test_calendar_api_endpoint(self):
        content = EVENTS_PY.read_text()
        assert 'def calendar_events' in content
        assert '/calendar' in content

    def test_api_returns_year_month(self):
        content = EVENTS_PY.read_text()
        assert '"year": year' in content
        assert '"month": month' in content

    def test_api_returns_events_list(self):
        content = EVENTS_PY.read_text()
        assert '"events": events' in content

    def test_api_includes_rsvp_counts(self):
        content = EVENTS_PY.read_text()
        assert 'rsvp_counts' in content
        assert 'RSVPStatus.REGISTERED' in content

    def test_api_includes_user_rsvp_status(self):
        content = EVENTS_PY.read_text()
        assert 'user_rsvps' in content
        assert 'user_rsvp' in content


# ── 4. Locale keys ──

class TestCalendarLocales:
    @pytest.fixture
    def en(self):
        return json.loads(EN_JSON.read_text())

    @pytest.fixture
    def it(self):
        return json.loads(IT_JSON.read_text())

    def test_en_calendar_section_exists(self, en):
        assert "calendar" in en

    def test_it_calendar_section_exists(self, it):
        assert "calendar" in it

    def test_en_has_required_keys(self, en):
        cal = en["calendar"]
        required = ["title", "subtitle", "tab_community", "tab_my_events",
                     "no_events", "no_my_events", "today", "free", "past",
                     "create_event", "prev_month", "next_month",
                     "mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        for key in required:
            assert key in cal, f"Missing en calendar key: {key}"

    def test_it_has_required_keys(self, it):
        cal = it["calendar"]
        required = ["title", "subtitle", "tab_community", "tab_my_events",
                     "no_events", "no_my_events", "today", "free", "past",
                     "create_event", "prev_month", "next_month",
                     "mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        for key in required:
            assert key in cal, f"Missing it calendar key: {key}"

    def test_en_nav_calendar(self, en):
        assert "calendar" in en["nav"]

    def test_it_nav_calendar(self, it):
        assert "calendar" in it["nav"]

    def test_it_day_names_are_italian(self, it):
        cal = it["calendar"]
        assert cal["mon"] == "Lun"
        assert cal["dom"] if "dom" in cal else cal["sun"] == "Dom"


# ── 5. Nav links ──

class TestCalendarNav:
    def test_desktop_nav_has_calendar(self):
        content = BASE_HTML.read_text()
        assert 'href="/calendar"' in content

    def test_mobile_nav_has_calendar(self):
        content = BASE_HTML.read_text()
        lines = content.split("\n")
        mobile_section = False
        found = False
        for line in lines:
            if "lg:hidden" in line:
                mobile_section = True
            if mobile_section and '/calendar' in line:
                found = True
                break
        assert found, "Calendar link not found in mobile nav"


# ── 6. Tab structure ──

class TestCalendarTabs:
    def test_community_tab_exists(self):
        content = CALENDAR_HTML.read_text()
        assert "tab === 'community'" in content

    def test_my_events_tab_exists(self):
        content = CALENDAR_HTML.read_text()
        assert "tab === 'my_events'" in content

    def test_tab_buttons_exist(self):
        content = CALENDAR_HTML.read_text()
        assert "tab_community" in content
        assert "tab_my_events" in content


# ── 7. Month navigation ──

class TestMonthNavigation:
    def test_prev_month_button(self):
        content = CALENDAR_HTML.read_text()
        assert "prevMonth()" in content

    def test_next_month_button(self):
        content = CALENDAR_HTML.read_text()
        assert "nextMonth()" in content

    def test_month_name_display(self):
        content = CALENDAR_HTML.read_text()
        assert "monthName" in content


# ── 8. RSVP integration ──

class TestCalendarRSVP:
    def test_rsvp_button_in_template(self):
        content = CALENDAR_HTML.read_text()
        assert "rsvp(ev.id)" in content

    def test_cancel_rsvp_button(self):
        content = CALENDAR_HTML.read_text()
        assert "cancelRsvp(ev.id)" in content

    def test_rsvp_status_badges(self):
        content = CALENDAR_HTML.read_text()
        assert "ev.user_rsvp === 'registered'" in content
        assert "ev.user_rsvp === 'waitlisted'" in content


# ── 9. Calendar grid ──

class TestCalendarGrid:
    def test_seven_column_grid(self):
        content = CALENDAR_HTML.read_text()
        assert "grid-cols-7" in content

    def test_day_headers(self):
        content = CALENDAR_HTML.read_text()
        assert "calendar.mon" in content
        assert "calendar.sun" in content

    def test_today_highlight(self):
        content = CALENDAR_HTML.read_text()
        assert "isToday(day)" in content

    def test_event_dots_on_days(self):
        content = CALENDAR_HTML.read_text()
        assert "eventsOnDay(day)" in content


# ── 10. Event card info ──

class TestEventCards:
    def test_shows_title(self):
        content = CALENDAR_HTML.read_text()
        assert "ev.title" in content

    def test_shows_time(self):
        content = CALENDAR_HTML.read_text()
        assert "formatTime(ev.event_start)" in content

    def test_shows_venue(self):
        content = CALENDAR_HTML.read_text()
        assert "ev.event_venue" in content

    def test_shows_price(self):
        content = CALENDAR_HTML.read_text()
        assert "ev.price" in content

    def test_shows_rsvp_count(self):
        content = CALENDAR_HTML.read_text()
        assert "ev.rsvp_count" in content

    def test_links_to_item_detail(self):
        content = CALENDAR_HTML.read_text()
        assert "'/item/' + ev.item_id" in content


# ── 11. API imports ──

class TestAPIImports:
    def test_imports_calendar_module(self):
        content = EVENTS_PY.read_text()
        assert "import calendar as cal_mod" in content

    def test_imports_datetime(self):
        content = EVENTS_PY.read_text()
        assert "from datetime import datetime, timezone" in content

    def test_imports_selectinload(self):
        content = EVENTS_PY.read_text()
        assert "selectinload" in content

    def test_imports_bhitem(self):
        content = EVENTS_PY.read_text()
        assert "from src.models.item import BHItem" in content


# ── 12. Alpine safety ──

class TestCalendarAlpineSafety:
    def test_no_t_in_xtext(self):
        content = CALENDAR_HTML.read_text()
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if 'x-text="' in stripped:
                idx = stripped.find('x-text="') + 8
                end = stripped.find('"', idx)
                if end > idx:
                    val = stripped[idx:end]
                    if "{{ t(" in val:
                        assert False, f"Line {i}: t() inside x-text: {val[:80]}"

    def test_no_t_in_onclick(self):
        content = CALENDAR_HTML.read_text()
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if '@click="' in stripped:
                idx = stripped.find('@click="') + 8
                end = stripped.find('"', idx)
                if end > idx:
                    val = stripped[idx:end]
                    if "{{ t(" in val:
                        assert False, f"Line {i}: t() inside @click: {val[:80]}"


# ── 13. Empty states ──

class TestEmptyStates:
    def test_no_events_message(self):
        content = CALENDAR_HTML.read_text()
        assert "calendar.no_events" in content

    def test_no_my_events_message(self):
        content = CALENDAR_HTML.read_text()
        assert "calendar.no_my_events" in content


# ── 14. Create event CTA ──

class TestCreateEventCTA:
    def test_create_event_link(self):
        content = CALENDAR_HTML.read_text()
        assert 'href="/list"' in content
        assert "calendar.create_event" in content
