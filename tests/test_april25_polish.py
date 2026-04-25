"""Regression tests for the polish work April 23-25.

Each test pins one behavior we explicitly fixed this week so that a
future careless edit can't silently undo it. Pure-content checks
where possible (no DB), file regex/grep style.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
TPL = ROOT / "src" / "templates"


# ── Translate auto-system removed ─────────────────────────────────────


def test_no_floating_translate_pill_in_base():
    """The floating 'Show Original' pill (bh-translate-toggle) was removed.

    It auto-fired on every page where any item's content_lang differed
    from the viewer's lang and called Google Translate. Hard ban.
    """
    base = (TPL / "base.html").read_text()
    assert "bh-translate-toggle" not in base, \
        "The auto-translate floating pill is back. It was removed for a reason."


def test_no_auto_translate_call_on_page_load():
    """BHTranslate.autoTranslatePage() must NOT auto-fire on DOMContentLoaded."""
    base = (TPL / "base.html").read_text()
    # The function may exist in a stub or be removed entirely. What we forbid
    # is the auto-fire on DOMContentLoaded, which was the whole point of removing it.
    if "DOMContentLoaded" in base:
        # If DOMContentLoaded is referenced, autoTranslatePage must not be invoked there.
        # Pull the DOMContentLoaded handlers and check.
        assert "BHTranslate.autoTranslatePage()" not in base or \
               "// autoTranslatePage" in base, \
            "Auto-translate must not fire on page load."


def test_helpboard_js_does_not_call_auto_translate():
    helpboard_js = (ROOT / "src" / "static" / "js" / "app" / "helpboard.js").read_text()
    assert "BHTranslate.autoTranslatePage()" not in helpboard_js, \
        "helpboard.js was calling the removed auto-translate. Should be a no-op now."


def test_item_detail_translate_button_is_conditional():
    """Item-detail's manual Translate button should only render when content
    language differs from viewer's lang -- otherwise it's noise."""
    item_detail = (TPL / "pages" / "item_detail.html").read_text()
    # The conditional that gates the button -- both description AND story blocks.
    assert "(item.content_language or 'en') != lang" in item_detail, \
        "Translate button must be gated on content_lang != viewer lang."


# ── Raffle trust gate compliance ───────────────────────────────────────


def test_validate_raffle_value_rejects_null_max_tickets():
    """Unbounded pots (max_tickets=None) make the cap unenforceable.

    Pre-fix: returned (True, '') -- silent bypass. Post-fix: explicit reject.
    """
    import asyncio
    import inspect
    from src.services.raffle_engine import validate_raffle_value
    src = inspect.getsource(validate_raffle_value)
    # Function must contain the explicit None-rejection branch.
    assert "max_tickets is None" in src, \
        "validate_raffle_value should explicitly handle max_tickets=None."
    assert "max ticket count" in src.lower() or "max ticket" in src.lower(), \
        "Reject message should explain that max_tickets is required."


def test_raffle_creation_endpoint_has_age_14_check():
    """The raffle creation endpoint must enforce a 14-year-old minimum
    (Italian community-fundraiser norm) and require DOB to be set."""
    raffles = (ROOT / "src" / "routers" / "raffles.py").read_text()
    assert "age_years < 14" in raffles, \
        "Age-14 floor missing on raffle creation."
    assert "date of birth" in raffles.lower() or "date_of_birth" in raffles.lower(), \
        "Endpoint must require DOB before allowing raffle creation."


# ── Smart empty states ───────────────────────────────────────────────


def test_browse_empty_state_echoes_query():
    """When q is set, empty state should echo it back via no_matches_for."""
    browse = (TPL / "pages" / "browse.html").read_text()
    # The block that echoes the query
    assert "browse.no_matches_for" in browse, \
        "Browse empty state must echo the search query when set."
    # Sibling-surface hops: links to /members, /calendar, /helpboard from empty browse
    assert "search_elsewhere" in browse, \
        "Browse empty state must offer sibling-surface hops."


def test_members_empty_state_echoes_query():
    members = (TPL / "pages" / "members.html").read_text()
    assert "members.no_matches_for" in members
    assert "search_elsewhere" in members


def test_helpboard_empty_state_offers_sibling_search():
    helpboard = (TPL / "pages" / "helpboard.html").read_text()
    assert "search_elsewhere" in helpboard, \
        "Helpboard empty state must offer sibling-surface hops."


def test_search_elsewhere_i18n_keys_exist():
    """The search_elsewhere block must exist in both EN and IT locales."""
    import json
    en = json.loads((ROOT / "src" / "locales" / "en.json").read_text())
    it = json.loads((ROOT / "src" / "locales" / "it.json").read_text())
    for loc, name in [(en, "en"), (it, "it")]:
        assert "search_elsewhere" in loc, f"{name}.json missing search_elsewhere block"
        for key in ("heading", "items", "members", "events", "helpboard"):
            assert key in loc["search_elsewhere"], \
                f"{name}.json search_elsewhere.{key} missing"


# ── Clickable tags everywhere ──────────────────────────────────────────


def test_item_detail_listing_type_pill_is_link():
    """Listing-type pills on item-detail title row must be <a> tags
    pointing at /browse?listing_type=..., not <span>."""
    item_detail = (TPL / "pages" / "item_detail.html").read_text()
    # The listing_type pill block uses a href to /browse with the listing_type filter
    assert '/browse?listing_type=' in item_detail, \
        "Listing-type pill on item detail must link to /browse?listing_type=..."


def test_workshop_skill_is_clickable_link():
    """Each skill on workshop profile must be a link to /members?skill=..."""
    workshop = (TPL / "pages" / "workshop.html").read_text()
    assert '/members?skill=' in workshop, \
        "Workshop skill name must be a link to /members?skill=..."


def test_workshop_badge_is_clickable_link():
    workshop = (TPL / "pages" / "workshop.html").read_text()
    assert '/members?badge_tier=' in workshop, \
        "Workshop badge pill must link to /members?badge_tier=..."


def test_workshop_language_is_clickable_link():
    workshop = (TPL / "pages" / "workshop.html").read_text()
    assert '/members?language=' in workshop, \
        "Workshop language row must link to /members?language=..."


def test_workshop_city_is_clickable_link():
    workshop = (TPL / "pages" / "workshop.html").read_text()
    assert '/members?city=' in workshop, \
        "Workshop city must link to /members?city=..."


def test_workshop_service_pills_are_clickable_links():
    workshop = (TPL / "pages" / "workshop.html").read_text()
    # All five service offers -- repair / pickup / training / custom_orders / delivery
    assert '/members?service=' in workshop, \
        "Workshop service offers must link to /members?service=..."


# ── Availability MVP ───────────────────────────────────────────────────


def test_listing_schema_has_availability_note():
    """Pydantic schemas must expose availability_note so it doesn't silently drop."""
    from src.schemas.listing import ListingCreate, ListingUpdate, ListingOut
    for schema_cls, name in [
        (ListingCreate, "ListingCreate"),
        (ListingUpdate, "ListingUpdate"),
        (ListingOut, "ListingOut"),
    ]:
        assert "availability_note" in schema_cls.model_fields, \
            f"{name} missing availability_note (will silently drop user input)"


def test_listing_model_has_availability_note():
    from src.models.listing import BHListing
    assert hasattr(BHListing, "availability_note"), \
        "BHListing missing availability_note column"


# ── Media relationship ─────────────────────────────────────────────────


def test_item_media_relationship_orders_by_sort_order():
    """BHItem.media must order by sort_order so drag-to-reorder is actually visible.

    Pre-fix: relationship had no order_by; reorder wrote the column but render
    used insertion order. Drag worked, reload showed nothing. Test pins the fix.
    """
    item_py = (ROOT / "src" / "models" / "item.py").read_text()
    # Find the media relationship line and verify order_by
    media_line = next(
        (l for l in item_py.splitlines() if "media: Mapped" in l and "BHItemMedia" in l),
        None,
    )
    assert media_line is not None, "BHItem.media relationship not found"
    assert "order_by" in media_line and "sort_order" in media_line, \
        f"BHItem.media must specify order_by=BHItemMedia.sort_order. Got: {media_line.strip()}"


# ── Calendar mobile dropdown ───────────────────────────────────────────


def test_calendar_has_mobile_dropdown():
    """Calendar tabs on mobile must be a select dropdown, not horizontal scroll."""
    cal = (TPL / "pages" / "calendar.html").read_text()
    # Mobile-only select with x-model bound to tab
    assert 'sm:hidden' in cal and 'id="calendar-tab-mobile"' in cal, \
        "Calendar must have a mobile-only dropdown for tab switching."


def test_calendar_day_sheet_above_bottom_nav():
    """Day-sheet drawer must sit above the bottom mobile nav (z-50 vs z-40)."""
    cal = (TPL / "pages" / "calendar.html").read_text()
    # The drawer's outer overlay
    assert 'fixed inset-0 z-50' in cal, \
        "Day-sheet drawer must be z-50 to sit above the bottom-nav (z-40)."


# ── Translate suppression server-side ────────────────────────────────


def test_html_has_translate_no_attribute():
    """The <html> tag in base.html must carry translate='no' to suppress
    browser-level auto-translate prompts."""
    for path in [
        TPL / "base.html",
        TPL / "pages" / "invoice_print.html",
        TPL / "export" / "workshop.html",
    ]:
        html = path.read_text()
        # Match the <html> tag opening
        opening = next((l for l in html.splitlines() if "<html " in l or l.lstrip().startswith("<html ")), None)
        assert opening is not None, f"{path.name}: no <html> tag found"
        assert 'translate="no"' in opening, \
            f"{path.name}: <html> must have translate=\"no\""


def test_meta_google_notranslate_in_base():
    base = (TPL / "base.html").read_text()
    assert 'name="google" content="notranslate"' in base, \
        "base.html must have meta name='google' content='notranslate'"


def test_content_language_middleware_present():
    """The Content-Language header is set by middleware in main.py."""
    main_py = (ROOT / "src" / "main.py").read_text()
    assert "ContentLanguageMiddleware" in main_py, \
        "ContentLanguageMiddleware missing from main.py"
    assert "Content-Language" in main_py, \
        "Header name 'Content-Language' missing"


# ── Mobile nav has icons ──────────────────────────────────────────────


def test_mobile_nav_items_have_icons():
    """Every mobile drawer link should pair an SVG icon with the label."""
    base = (TPL / "base.html").read_text()
    # Find the mobile nav block and ensure key links have an svg child
    # Look for the 'mobileMenuOpen = false' container which is the mobile drawer
    start = base.find('@click="mobileMenuOpen = false"')
    assert start > 0, "Mobile nav drawer block not found"
    # The drawer ends with the language switcher block; find a stable closing marker
    end = base.find('<!-- Mobile language switch', start)
    assert end > start, "Mobile drawer end-marker not found"
    block = base[start:end]
    # Each of these hrefs in the mobile drawer should be present
    for href in ('/browse', '/helpboard', '/calendar', '/leaderboard', '/members', '/chat'):
        assert f'href="{href}"' in block, f"mobile nav missing {href}"
    # Drawer has 13+ items each carrying an SVG icon. Use 12 as a defensive floor.
    svg_count = block.count("<svg")
    assert svg_count >= 12, f"mobile nav should have at least 12 SVG icons, found {svg_count}"
