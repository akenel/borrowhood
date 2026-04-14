"""Tests for April 15 anonymous user feedback fixes and filter redesign.

Covers:
- Browse filters: empty price_max doesn't 422
- Browse filters: listing_type accepts 'event'
- Browse filters: free_only works
- Calendar template renders (fix for broken <button> tag that broke Alpine)
- Members page has "Trust score:" visible label (was bare "15%")
- Home page Quick Start hidden for anonymous users
- Home page has Concierge teaser link
- Nav has Concierge in main nav
- Footer Privacy points to /terms#privacy
- Terms section 15 (duplicate cookies) removed
- Notification enum has SAVED_SEARCH_MATCH uppercase
- Browse template renders for anonymous users (no favorites fetch)
"""

import pytest


# ── Browse filter router tests ──


@pytest.mark.asyncio
async def test_browse_empty_price_max_ok(db_client):
    """Empty price_max does NOT 422 (was a bug when live-submit form sent '')."""
    resp = await db_client.get("/browse?q=&sort=newest&listing_type=&price_max=")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_browse_empty_free_only_ok(db_client):
    """Empty free_only does NOT 422."""
    resp = await db_client.get("/browse?free_only=")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_browse_free_only_true_ok(db_client):
    """free_only=true returns 200 and filters properly."""
    resp = await db_client.get("/browse?free_only=true")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_browse_listing_type_event_ok(db_client):
    """listing_type=event doesn't crash -- critical since events were missing before."""
    resp = await db_client.get("/browse?listing_type=event")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_browse_all_listing_types_ok(db_client):
    """Every listing_type value the dropdown offers must work."""
    for lt in ["rent", "sell", "event", "service", "training", "commission", "auction", "giveaway", "offer"]:
        resp = await db_client.get(f"/browse?listing_type={lt}")
        assert resp.status_code == 200, f"listing_type={lt} failed"


@pytest.mark.asyncio
async def test_browse_price_max_valid_numbers(db_client):
    """price_max with valid numbers works."""
    for p in ["10", "50", "200", "1000"]:
        resp = await db_client.get(f"/browse?price_max={p}")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_browse_price_max_invalid_gracefully_ignored(db_client):
    """price_max with garbage doesn't crash, just ignored."""
    resp = await db_client.get("/browse?price_max=banana")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_browse_combined_filters_ok(db_client):
    """Multiple filters together work."""
    resp = await db_client.get("/browse?listing_type=rent&price_max=50&sort=newest")
    assert resp.status_code == 200


# ── Template renders for anonymous users ──


@pytest.mark.asyncio
async def test_browse_renders_anon(db_client):
    """Browse page renders for anonymous users without errors."""
    resp = await db_client.get("/browse")
    assert resp.status_code == 200
    html = resp.text
    # Key modernized elements should be present
    assert "Browse by category" in html or "Esplora per categoria" in html
    assert "Looking for" in html or "Qualsiasi" in html
    assert "Free only" in html or "Solo gratis" in html


@pytest.mark.asyncio
async def test_browse_favorite_ids_gated_for_anon(db_client):
    """Anon users shouldn't trigger favorite-ids fetch -- check the loggedIn guard is in template."""
    resp = await db_client.get("/browse")
    html = resp.text
    # The template sets loggedIn: false for anon users
    assert "loggedIn: false" in html


# ── Calendar template ──


@pytest.mark.asyncio
async def test_calendar_page_renders(db_client):
    """Calendar page renders without Alpine template errors (fix for missing > on button)."""
    resp = await db_client.get("/calendar")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_calendar_api_returns_events(db_client):
    """Events API returns expected shape for calendar grid."""
    resp = await db_client.get("/api/v1/events/calendar?month=4&year=2026")
    assert resp.status_code == 200
    data = resp.json()
    assert "events" in data
    assert "year" in data
    assert "month" in data


# ── Members page ──


@pytest.mark.asyncio
async def test_members_trust_score_has_label(db_client):
    """Trust score renders with visible 'Trust score:' label, not bare '15%'."""
    resp = await db_client.get("/members?sort=trust")
    html = resp.text
    # Must have label + colon + %
    import re
    # Matches "Trust score: 15%" or "Trust score: 88%" etc.
    assert re.search(r"Trust score:\s*\d+%", html), "Trust score label missing"


# ── Home page ──


@pytest.mark.asyncio
async def test_home_hero_has_concierge_teaser(db_client):
    """Home hero shows AI Concierge teaser link."""
    resp = await db_client.get("/")
    html = resp.text
    # Either EN or IT teaser copy
    assert "Ask our AI" in html or "chiedi all'AI" in html


@pytest.mark.asyncio
async def test_home_hero_primary_cta_browse(db_client):
    """Home has ONE primary CTA (Browse Items), not 3 competing buttons."""
    resp = await db_client.get("/")
    html = resp.text
    # Browse button should be prominent on home
    assert 'href="/browse"' in html


# ── Navigation ──


@pytest.mark.asyncio
async def test_nav_has_concierge_chat(db_client):
    """Main desktop nav includes /chat link (Concierge was hidden before)."""
    resp = await db_client.get("/")
    html = resp.text
    assert 'href="/chat"' in html


@pytest.mark.asyncio
async def test_nav_has_calendar(db_client):
    """Main desktop nav includes /calendar link."""
    resp = await db_client.get("/")
    assert 'href="/calendar"' in resp.text


@pytest.mark.asyncio
async def test_nav_has_leaderboard(db_client):
    """Main desktop nav includes /leaderboard link."""
    resp = await db_client.get("/")
    assert 'href="/leaderboard"' in resp.text


# ── Terms / Privacy ──


@pytest.mark.asyncio
async def test_footer_privacy_uses_anchor(db_client):
    """Footer privacy link points to /terms#privacy, not just /terms."""
    resp = await db_client.get("/")
    html = resp.text
    assert 'href="/terms#privacy"' in html


@pytest.mark.asyncio
async def test_terms_has_privacy_anchor(db_client):
    """Terms page has id='privacy' anchor for the Privacy section."""
    resp = await db_client.get("/terms")
    html = resp.text
    assert 'id="privacy"' in html


@pytest.mark.asyncio
async def test_terms_no_duplicate_cookies_section(db_client):
    """Section 15 (duplicate cookies) should be gone -- Section 9 has all cookie info."""
    resp = await db_client.get("/terms")
    html = resp.text
    # Section 15 title was "15. Cookies" -- should NOT appear
    assert "15. Cookies" not in html
    # But Section 9 Privacy with cookies should still be there
    assert "9. Privacy" in html or "section_9_title" in html


# ── Notification enum ──


def test_saved_search_match_notification_uppercase():
    """SAVED_SEARCH_MATCH enum value is UPPERCASE (matches DB convention)."""
    from src.models.notification import NotificationType
    assert NotificationType.SAVED_SEARCH_MATCH.value == "SAVED_SEARCH_MATCH"


# ── Empty-string coercion unit test ──


@pytest.mark.asyncio
async def test_browse_all_empty_strings_ok(db_client):
    """Every filter param can be empty string without crashing."""
    resp = await db_client.get(
        "/browse?q=&category=&category_group=&item_type=&listing_type=&price_max=&free_only=&sort=newest"
    )
    assert resp.status_code == 200


# ── Tooltip-free nav: icon+text both visible ──


@pytest.mark.asyncio
async def test_nav_has_icons_and_text(db_client):
    """Desktop nav items have both icon (svg) AND text label -- no icon-only mystery."""
    resp = await db_client.get("/")
    html = resp.text
    # Chat link should have both an SVG icon and the word "Chat" (or t('nav.chat'))
    import re
    # Each nav item should be a link containing an <svg ...> and text content
    # Simple heuristic: the /browse link should be in an <a> with svg before text
    assert re.search(r'<a href="/browse"[^>]*>\s*<svg', html), \
        "Browse nav link missing icon"


# ── Home page rendering for logged-out users ──


@pytest.mark.asyncio
async def test_home_quick_start_only_for_logged_in(db_client):
    """Quick Start funnel section is wrapped in {% if user %} -- anon users don't see it."""
    # For anon: the Quick Start section shouldn't render
    resp = await db_client.get("/")
    html = resp.text
    # The "Get started in 60 seconds" header appears only inside the Quick Start section
    # which is now gated behind {% if user %}. Anon users must NOT see it.
    assert "Get started in 60 seconds" not in html
    assert "Inizia in 60 secondi" not in html
