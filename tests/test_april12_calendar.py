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
        assert "'/items/' + ev.item_slug" in content


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


# ── 15. API endpoint structure ──

class TestCalendarAPIStructure:
    def test_api_fetches_active_and_expired_events(self):
        content = EVENTS_PY.read_text()
        assert "ListingStatus.ACTIVE" in content
        assert "ListingStatus.EXPIRED" in content

    def test_api_uses_month_boundaries(self):
        content = EVENTS_PY.read_text()
        assert "monthrange" in content

    def test_api_includes_owner_info(self):
        content = EVENTS_PY.read_text()
        assert '"owner_name"' in content
        assert '"owner_slug"' in content
        assert '"owner_avatar"' in content

    def test_api_includes_item_slug(self):
        content = EVENTS_PY.read_text()
        assert '"item_slug"' in content

    def test_api_includes_event_fields(self):
        content = EVENTS_PY.read_text()
        for field in ['"event_start"', '"event_end"', '"event_venue"',
                      '"event_address"', '"event_link"', '"price"',
                      '"capacity"', '"rsvp_count"', '"image"', '"day"']:
            assert field in content, f"Missing field in API response: {field}"

    def test_api_loads_media_for_images(self):
        content = EVENTS_PY.read_text()
        assert "BHItem.media" in content
        assert "media_type" in content

    def test_api_handles_missing_month_year(self):
        content = EVENTS_PY.read_text()
        assert "if not month:" in content
        assert "if not year:" in content

    def test_api_handles_anonymous_users(self):
        content = EVENTS_PY.read_text()
        assert "get_current_user_token" in content
        assert "user_rsvps = {}" in content


# ── 16. Calendar template data flow ──

class TestCalendarDataFlow:
    def test_fetches_from_correct_api(self):
        content = CALENDAR_HTML.read_text()
        assert "/api/v1/events/calendar" in content

    def test_passes_month_year_params(self):
        content = CALENDAR_HTML.read_text()
        assert "month=" in content
        assert "year=" in content

    def test_rsvp_posts_to_correct_endpoint(self):
        content = CALENDAR_HTML.read_text()
        assert "/api/v1/events/" in content
        assert "/rsvp" in content

    def test_cancel_uses_delete_method(self):
        content = CALENDAR_HTML.read_text()
        assert "method: 'DELETE'" in content

    def test_rsvp_uses_post_method(self):
        content = CALENDAR_HTML.read_text()
        assert "method: 'POST'" in content

    def test_redirects_to_login_on_401(self):
        content = CALENDAR_HTML.read_text()
        assert "r.status === 401" in content
        assert "'/login'" in content

    def test_reloads_month_after_rsvp(self):
        content = CALENDAR_HTML.read_text()
        rsvp_func = content[content.find("async rsvp("):content.find("async cancelRsvp(")]
        assert "loadMonth()" in rsvp_func

    def test_reloads_month_after_cancel(self):
        content = CALENDAR_HTML.read_text()
        cancel_func = content[content.find("async cancelRsvp("):]
        assert "loadMonth()" in cancel_func


# ── 17. Alpine.js computed properties ──

class TestAlpineComputedProps:
    def test_community_events_filter(self):
        content = CALENDAR_HTML.read_text()
        assert "communityEvents" in content

    def test_my_events_filter(self):
        content = CALENDAR_HTML.read_text()
        assert "myEvents" in content
        assert "e.user_rsvp" in content

    def test_display_events_switches_on_tab(self):
        content = CALENDAR_HTML.read_text()
        assert "displayEvents" in content

    def test_events_on_day_function(self):
        content = CALENDAR_HTML.read_text()
        assert "eventsOnDay(day)" in content
        assert "e.day === day" in content

    def test_is_past_function(self):
        content = CALENDAR_HTML.read_text()
        assert "isPast(day)" in content

    def test_format_time_function(self):
        content = CALENDAR_HTML.read_text()
        assert "formatTime(iso)" in content
        assert "toLocaleString" in content

    def test_format_time_short_function(self):
        content = CALENDAR_HTML.read_text()
        assert "formatTimeShort(iso)" in content
        assert "toLocaleTimeString" in content


# ── 18. Accessibility & UX ──

class TestCalendarAccessibility:
    def test_prev_month_has_title(self):
        content = CALENDAR_HTML.read_text()
        assert "calendar.prev_month" in content

    def test_next_month_has_title(self):
        content = CALENDAR_HTML.read_text()
        assert "calendar.next_month" in content

    def test_event_links_to_detail(self):
        content = CALENDAR_HTML.read_text()
        assert "'/items/' + ev.item_slug" in content

    def test_loading_spinner(self):
        content = CALENDAR_HTML.read_text()
        assert "animate-spin" in content
        assert "loading" in content

    def test_sold_out_button_disabled(self):
        content = CALENDAR_HTML.read_text()
        assert ":disabled=" in content
        assert "ev.rsvp_count >= ev.capacity" in content

    def test_past_events_show_label(self):
        content = CALENDAR_HTML.read_text()
        assert "calendar.past" in content
        assert "ev.status !== 'active'" in content

    def test_free_events_labeled(self):
        content = CALENDAR_HTML.read_text()
        assert "calendar.free" in content
        assert "!ev.price" in content

    def test_click_stop_propagation_on_rsvp(self):
        content = CALENDAR_HTML.read_text()
        assert "@click.prevent.stop" in content

    def test_mobile_dots_desktop_chips(self):
        content = CALENDAR_HTML.read_text()
        assert "hidden sm:block" in content
        assert "sm:hidden" in content

    def test_event_overflow_indicator(self):
        content = CALENDAR_HTML.read_text()
        assert "eventsOnDay(day).length > 3" in content


# ── 19. Locale consistency ──

class TestLocaleConsistency:
    def test_en_it_calendar_keys_match(self):
        en = json.loads(EN_JSON.read_text())
        it = json.loads(IT_JSON.read_text())
        en_keys = set(en["calendar"].keys())
        it_keys = set(it["calendar"].keys())
        missing_in_it = en_keys - it_keys
        missing_in_en = it_keys - en_keys
        assert not missing_in_it, f"Keys in en but not it: {missing_in_it}"
        assert not missing_in_en, f"Keys in it but not en: {missing_in_en}"

    def test_en_it_nav_keys_match(self):
        en = json.loads(EN_JSON.read_text())
        it = json.loads(IT_JSON.read_text())
        en_nav = set(en["nav"].keys())
        it_nav = set(it["nav"].keys())
        assert en_nav == it_nav, f"Nav key mismatch: en-it={en_nav - it_nav}, it-en={it_nav - en_nav}"


# ── 20. Calendar grid math ──

class TestCalendarGridMath:
    def test_first_day_offset_calculation(self):
        content = CALENDAR_HTML.read_text()
        assert "firstDayOffset" in content
        assert "getDay()" in content

    def test_days_in_month_calculation(self):
        content = CALENDAR_HTML.read_text()
        assert "daysInMonth" in content
        assert "new Date(this.year, this.month, 0).getDate()" in content

    def test_empty_cells_for_offset(self):
        content = CALENDAR_HTML.read_text()
        assert "x-for=\"_ in firstDayOffset\"" in content


# ── 21. Seed data script ──

class TestSeedDataScript:
    def test_seed_script_exists(self):
        assert Path("scripts/seed-calendar-events.sql").exists()

    def test_seed_has_10_items(self):
        content = Path("scripts/seed-calendar-events.sql").read_text()
        assert content.count("INSERT INTO bh_item") == 10

    def test_seed_has_10_listings(self):
        content = Path("scripts/seed-calendar-events.sql").read_text()
        assert content.count("INSERT INTO bh_listing") == 10

    def test_seed_uses_uppercase_enums(self):
        content = Path("scripts/seed-calendar-events.sql").read_text()
        assert "'EVENT'" in content
        assert "'ACTIVE'" in content
        assert "'REGISTERED'" in content
        assert "'event'" not in content.split("-- ")[1]  # After first comment


# ── 22. Share button on calendar cards ──

ITEM_DETAIL_HTML = Path("src/templates/pages/item_detail.html")
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


class TestCalendarShareButton:
    def test_share_button_exists(self):
        content = CALENDAR_HTML.read_text()
        assert "bhShare(" in content

    def test_share_uses_data_attributes(self):
        content = CALENDAR_HTML.read_text()
        assert "$el.dataset.name" in content
        assert "$el.dataset.url" in content

    def test_share_url_points_to_item_detail(self):
        content = CALENDAR_HTML.read_text()
        assert "'/items/' + ev.item_slug" in content
        assert "lapiazza.app/items/" in content

    def test_share_title_from_data_attr_not_inline(self):
        content = CALENDAR_HTML.read_text()
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if "bhShare(" in line and "ev.title" in line:
                assert False, f"Line {i}: bhShare uses ev.title inline instead of data attribute"


# ── 23. OG meta tags ──

class TestOGMetaTags:
    def test_base_has_twitter_image(self):
        content = BASE_HTML.read_text()
        assert 'twitter:image' in content

    def test_base_og_type_uses_context_var(self):
        content = BASE_HTML.read_text()
        assert "og_type | default" in content

    def test_item_detail_no_duplicate_og_type(self):
        content = ITEM_DETAIL_HTML.read_text()
        assert content.count('og:type') <= 1

    def test_calendar_route_has_og_tags(self):
        content = PAGES_PY.read_text()
        cal_section = content[content.find("def calendar_page"):content.find("def calendar_page") + 500]
        assert "og_title" in cal_section
        assert "og_description" in cal_section

    def test_item_detail_passes_og_type(self):
        content = PAGES_PY.read_text()
        start = content.find("def item_detail")
        end = content.find("\n@router", start + 1)
        detail_section = content[start:end]
        assert 'og_type="product"' in detail_section


# ── 24. Rich event OG descriptions ──

class TestEventOGDescription:
    def test_og_desc_builder_handles_events(self):
        content = PAGES_PY.read_text()
        func = content[content.find("def _og_item_desc"):content.find("\ndef ", content.find("def _og_item_desc") + 1)]
        assert "is_event" in func
        assert "event_start" in func
        assert "event_venue" in func

    def test_og_desc_includes_date_for_events(self):
        content = PAGES_PY.read_text()
        func = content[content.find("def _og_item_desc"):content.find("\ndef ", content.find("def _og_item_desc") + 1)]
        assert "strftime" in func

    def test_og_desc_includes_venue_for_events(self):
        content = PAGES_PY.read_text()
        func = content[content.find("def _og_item_desc"):content.find("\ndef ", content.find("def _og_item_desc") + 1)]
        assert "event_venue" in func
        assert "event_address" in func

    def test_og_desc_shows_free_for_no_price_events(self):
        content = PAGES_PY.read_text()
        func = content[content.find("def _og_item_desc"):content.find("\ndef ", content.find("def _og_item_desc") + 1)]
        assert '"Free"' in func

    def test_og_desc_uses_cest_timezone(self):
        content = PAGES_PY.read_text()
        func = content[content.find("def _og_item_desc"):content.find("\ndef ", content.find("def _og_item_desc") + 1)]
        assert "astimezone" in func
        assert "hours=2" in func

    def test_og_desc_non_events_unchanged(self):
        content = PAGES_PY.read_text()
        func = content[content.find("def _og_item_desc"):content.find("\ndef ", content.find("def _og_item_desc") + 1)]
        assert "if not is_event" in func


# ── 25. Media type fix in calendar API ──

class TestMediaTypeFix:
    def test_calendar_api_checks_photo_enum(self):
        content = EVENTS_PY.read_text()
        assert '"photo"' in content or "'photo'" in content

    def test_calendar_api_does_not_use_startswith_image(self):
        content = EVENTS_PY.read_text()
        cal_section = content[content.find("def calendar_events"):]
        assert 'startswith("image")' not in cal_section


# ── 26. OG tags on all shareable pages ──

class TestAllShareablePages:
    def test_base_has_all_required_og_tags(self):
        content = BASE_HTML.read_text()
        for tag in ["og:site_name", "og:type", "og:title", "og:description", "og:image", "og:url"]:
            assert tag in content, f"Missing {tag} in base.html"

    def test_base_has_all_required_twitter_tags(self):
        content = BASE_HTML.read_text()
        for tag in ["twitter:card", "twitter:title", "twitter:description", "twitter:image"]:
            assert tag in content, f"Missing {tag} in base.html"

    def test_twitter_image_uses_og_image_var(self):
        content = BASE_HTML.read_text()
        lines = content.split("\n")
        for line in lines:
            if "twitter:image" in line:
                assert "og_image" in line, "twitter:image should use og_image context var"
                break

    def test_workshop_page_has_og_tags(self):
        content = PAGES_PY.read_text()
        start = content.find("def workshop_profile")
        end = content.find("\n@router", start + 1)
        ws_section = content[start:end]
        assert "og_title" in ws_section
        assert "og_description" in ws_section
        assert "og_image" in ws_section
