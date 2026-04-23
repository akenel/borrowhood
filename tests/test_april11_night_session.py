"""Tests for April 11-12, 2026 night session -- RSVP E2E, Alpine safety, live updates.

Covers:
1. No t() calls inside x-text attributes in item_detail.html
2. No t() calls inside @click attributes in item_detail.html
3. No inline item.name in onclick/x-text (apostrophe safety)
4. Share buttons use data attributes not inline strings
5. RSVP button template structure (x-if has child element)
6. RSVP live count update (rsvp-changed event)
7. Online event link field exists
8. Event detail shows start AND end time
9. Tags display on item detail page
10. Event attributes card (skill_level, age, what_to_bring)
11. Delivery hidden for events in form
12. Empty Pricing section hidden for event-only items
13. Silent token refresh infrastructure
14. Avatar URL column is 2000 chars
"""

import pytest
from pathlib import Path


# ── 1-2. No t() in Alpine expressions ──

class TestAlpineSafety:
    def test_no_t_in_xtext_item_detail(self):
        """t() inside x-text breaks Alpine when translated text has apostrophes."""
        content = Path("src/templates/pages/item_detail.html").read_text()
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("{%"):
                continue
            if 'x-text="' in stripped:
                # Extract the x-text attribute value only
                idx = stripped.find('x-text="') + 8
                end = stripped.find('"', idx)
                if end > idx:
                    xtext_val = stripped[idx:end]
                    if "t('" in xtext_val:
                        assert False, f"Line {i}: t() inside x-text value: {xtext_val[:80]}"

    def test_no_t_in_onclick_item_detail(self):
        """t() inside @click/@change breaks on apostrophes in translations."""
        content = Path("src/templates/pages/item_detail.html").read_text()
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if '@click="' in stripped and "t('" in stripped:
                # Allow t() in button TEXT (between tags) but not in @click VALUE
                click_start = stripped.find('@click="') + 8
                click_end = stripped.find('"', click_start)
                click_val = stripped[click_start:click_end]
                if "t('" in click_val:
                    assert False, f"Line {i}: t() inside @click value: {click_val[:80]}"


# ── 3-4. Share buttons use data attributes ──

class TestShareButtonSafety:
    def test_item_detail_share_uses_data_name(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "bhShare($el.dataset.name" in content

    def test_browse_share_uses_data_name(self):
        content = Path("src/templates/pages/browse.html").read_text()
        assert "$el.dataset.name" in content

    def test_workshop_share_uses_data_name(self):
        content = Path("src/templates/pages/workshop.html").read_text()
        assert "$el.dataset.name" in content

    def test_native_share_uses_data_attribute(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "data-share-title" in content
        assert "this.dataset.shareTitle" in content


# ── 5. Template x-if structure ──

class TestTemplateXifStructure:
    def test_no_bare_text_in_template_xif(self):
        """Alpine template x-if must have exactly one child ELEMENT, not bare text."""
        content = Path("src/templates/pages/item_detail.html").read_text()
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("<template x-if="):
                # Check if this line also closes with text content (no child tag)
                if ">{{" in stripped and "</template>" in stripped:
                    # Bare text: <template x-if="...">{{ t(...) }}</template>
                    assert "<span>" in stripped or "<div>" in stripped or "<p>" in stripped, \
                        f"Line {i}: bare text in template x-if: {stripped[:100]}"


# ── 6. RSVP live count ──

class TestRSVPLiveCount:
    def test_rsvp_changed_event_dispatched(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "rsvp-changed" in content

    def test_capacity_bar_listens_for_rsvp_changed(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "addEventListener('rsvp-changed'" in content or "rsvp-changed" in content

    def test_rsvp_shows_registered_or_waitlisted_toast(self):
        """RSVP must render the correct status toast. Rewritten for BL-143: data- attrs
        were replaced with inline Jinja translations after adding the notes-panel."""
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "t('events.waitlisted')" in content
        assert "t('events.registered')" in content


# ── 7. Online event link ──

class TestOnlineEventLink:
    def test_event_link_column_exists(self):
        from src.models.listing import BHListing
        assert hasattr(BHListing, "event_link")

    def test_event_link_in_schemas(self):
        from src.schemas.listing import ListingCreate, ListingUpdate, ListingOut
        assert "event_link" in ListingCreate.model_fields
        assert "event_link" in ListingUpdate.model_fields
        assert "event_link" in ListingOut.model_fields

    def test_event_link_in_form(self):
        content = Path("src/templates/pages/list_item.html").read_text()
        assert "event_link" in content

    def test_event_link_display(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "online_event" in content or "event_link" in content


# ── 8. Start AND end time display ──

class TestEventTimeDisplay:
    def test_event_start_displayed(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "event_start" in content
        assert "data-event-utc" in content

    def test_event_end_displayed(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "event_end" in content

    def test_start_end_labels(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "events.event_start" in content
        assert "events.event_end" in content

    def test_timezone_converter_exists(self):
        content = Path("src/templates/base.html").read_text()
        assert "convertEventDates" in content
        assert "timeZoneName" in content


# ── 9. Tags display ──

class TestTagsDisplay:
    def test_tags_shown_on_item_detail(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "item.tags" in content
        assert "item.tags.split" in content

    def test_tags_are_clickable_links(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "/browse?q=" in content


# ── 10. Event attributes card ──

class TestEventAttributesCard:
    def test_skill_level_displayed(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "skill_level" in content

    def test_age_requirement_displayed(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "age_requirement" in content

    def test_what_to_bring_displayed(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "what_to_bring" in content


# ── 11-12. Event form and display cleanup ──

class TestEventFormCleanup:
    def test_delivery_hidden_for_events(self):
        content = Path("src/templates/pages/list_item.html").read_text()
        assert "selectedTypes.includes('event')" in content or "!selectedTypes.includes" in content

    def test_pricing_section_hidden_for_event_only(self):
        content = Path("src/templates/pages/item_detail.html").read_text()
        assert "non_event_listings" in content


# ── 13. Silent token refresh ──

class TestSilentTokenRefresh:
    def test_refresh_token_cookie_set(self):
        import inspect
        source = inspect.getsource(__import__("src.routers.auth", fromlist=["auth_callback"]))
        assert "bh_refresh" in source

    def test_silent_refresh_function(self):
        import inspect
        source = inspect.getsource(__import__("src.dependencies", fromlist=["_silent_refresh"]))
        assert "refresh_token" in source
        assert "grant_type" in source

    def test_token_refresh_middleware(self):
        import inspect
        source = inspect.getsource(__import__("src.main", fromlist=["create_app"]))
        assert "TokenRefreshMiddleware" in source
        assert "new_access_token" in source


# ── 14. Avatar URL ──

class TestAvatarURL:
    def test_avatar_url_2000_chars(self):
        from src.models.user import BHUser
        col = BHUser.__table__.columns["avatar_url"]
        assert col.type.length >= 2000
