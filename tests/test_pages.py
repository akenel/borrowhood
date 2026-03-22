"""Page route tests -- all HTML pages must return correct status and content.

Tests are split into:
- DB-independent: static pages, forms, terms (always run)
- DB-dependent: browse, item detail, workshop (need running Postgres with seed data)

DB-dependent tests are marked with @needs_db and skip gracefully when no DB is available.
"""

import pytest
import re

# Marker for tests that need a running database with seed data
needs_db = pytest.mark.skipif(
    True,  # Flip to False when running with local Postgres
    reason="Requires running Postgres with seed data",
)


# ═══════════════════════════════════════════════════════════════
# DB-INDEPENDENT TESTS (always pass, no Postgres needed)
# ═══════════════════════════════════════════════════════════════


# --- List Item Page ---

@pytest.mark.asyncio
async def test_list_item_returns_200(client):
    """List item page should return 200."""
    resp = await client.get("/list")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_item_has_form(client):
    """List item page should have the form fields."""
    resp = await client.get("/list")
    assert "name" in resp.text
    assert "category" in resp.text


@pytest.mark.asyncio
async def test_list_item_i18n_it(client):
    """List item page in Italian should use Italian labels."""
    resp = await client.get("/list?lang=it")
    assert "Pubblica un Oggetto" in resp.text


# --- Dashboard Page ---

@pytest.mark.asyncio
async def test_dashboard_returns_200(client):
    """Dashboard page should return 200."""
    resp = await client.get("/dashboard")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_dashboard_has_tabs(client):
    """Dashboard should have item and rental tabs."""
    resp = await client.get("/dashboard")
    assert "My Items" in resp.text or "My Dashboard" in resp.text


# --- Terms Page ---

@pytest.mark.asyncio
async def test_terms_returns_200(client):
    """Terms page should return 200."""
    resp = await client.get("/terms")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_terms_has_sections(client):
    """Terms page should have key sections."""
    resp = await client.get("/terms")
    assert "What La Piazza Is" in resp.text
    assert "Community Code of Conduct" in resp.text
    assert "Prohibited Content" in resp.text
    assert "Privacy" in resp.text


@pytest.mark.asyncio
async def test_terms_i18n_it(client):
    """Terms page in Italian should use Italian text."""
    resp = await client.get("/terms?lang=it")
    assert "Codice di Condotta della Comunità" in resp.text


@pytest.mark.asyncio
async def test_terms_has_acceptance(client):
    """Terms page should have the acceptance statement."""
    resp = await client.get("/terms")
    assert "By creating an account" in resp.text


# --- Help Board Page ---

@pytest.mark.asyncio
async def test_helpboard_returns_200(client):
    """Help Board page should return 200."""
    resp = await client.get("/helpboard")
    assert resp.status_code == 200


# --- Members Page ---

@needs_db
@pytest.mark.asyncio
async def test_members_returns_200(client):
    """Members page should return 200."""
    resp = await client.get("/members")
    assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════════
# DB-DEPENDENT TESTS (need Postgres + seed data)
# ═══════════════════════════════════════════════════════════════


# --- Home Page ---

@needs_db
@pytest.mark.asyncio
async def test_home_returns_200(client):
    """Home page should return 200."""
    resp = await client.get("/")
    assert resp.status_code == 200


@needs_db
@pytest.mark.asyncio
async def test_home_has_app_name(client):
    """Home page should contain the app name."""
    resp = await client.get("/")
    assert "La Piazza" in resp.text


@needs_db
@pytest.mark.asyncio
async def test_home_has_hero_title_en(client):
    """Home page should show English hero title."""
    resp = await client.get("/")
    assert "The Town Square is Open" in resp.text


@needs_db
@pytest.mark.asyncio
async def test_home_has_hero_title_it(client):
    """Home page in Italian should show Italian hero title."""
    resp = await client.get("/?lang=it")
    assert "La Piazza del Paese" in resp.text or "piazza" in resp.text.lower()


@needs_db
@pytest.mark.asyncio
async def test_home_has_stats(client):
    """Home page should show listing and member counts."""
    resp = await client.get("/")
    assert "Active Listings" in resp.text
    assert "Members" in resp.text


@needs_db
@pytest.mark.asyncio
async def test_home_has_how_it_works(client):
    """Home page should show How It Works section."""
    resp = await client.get("/")
    assert "How It Works" in resp.text


@needs_db
@pytest.mark.asyncio
async def test_home_sets_lang_cookie(client):
    """Switching language should set bh_lang cookie."""
    resp = await client.get("/?lang=it")
    set_cookie = resp.headers.get("set-cookie", "")
    assert "bh_lang=it" in set_cookie


# --- Browse Page ---

@needs_db
@pytest.mark.asyncio
async def test_browse_returns_200(client):
    """Browse page should return 200."""
    resp = await client.get("/browse")
    assert resp.status_code == 200


@needs_db
@pytest.mark.asyncio
async def test_browse_has_search(client):
    """Browse page should have a search input."""
    resp = await client.get("/browse")
    assert 'name="q"' in resp.text


@needs_db
@pytest.mark.asyncio
async def test_browse_has_filters(client):
    """Browse page should have category and type filters."""
    resp = await client.get("/browse")
    assert 'name="category"' in resp.text
    assert 'name="item_type"' in resp.text
    assert 'name="sort"' in resp.text


@needs_db
@pytest.mark.asyncio
async def test_browse_shows_items(client):
    """Browse page should show item cards (requires seed data)."""
    resp = await client.get("/browse")
    assert '/items/' in resp.text


@needs_db
@pytest.mark.asyncio
async def test_browse_i18n_it(client):
    """Browse page in Italian should use Italian labels."""
    resp = await client.get("/browse?lang=it")
    assert "Esplora" in resp.text


@needs_db
@pytest.mark.asyncio
async def test_browse_search_filter(client):
    """Browse page search should filter results."""
    resp = await client.get("/browse?q=cookie")
    assert resp.status_code == 200


@needs_db
@pytest.mark.asyncio
async def test_browse_sort_oldest(client):
    """Browse page should accept sort parameter."""
    resp = await client.get("/browse?sort=oldest")
    assert resp.status_code == 200


# --- Item Detail Page ---

@needs_db
@pytest.mark.asyncio
async def test_item_detail_returns_200(client):
    """Item detail page should return 200 for a valid slug."""
    browse = await client.get("/browse")
    match = re.search(r'href="/items/([^"]+)"', browse.text)
    assert match, "No item links found on browse page"
    resp = await client.get(f"/items/{match.group(1)}")
    assert resp.status_code == 200


@needs_db
@pytest.mark.asyncio
async def test_item_detail_has_breadcrumb(client):
    """Item detail should have breadcrumb navigation."""
    browse = await client.get("/browse")
    match = re.search(r'href="/items/([^"]+)"', browse.text)
    resp = await client.get(f"/items/{match.group(1)}")
    assert "Home" in resp.text
    assert "Browse" in resp.text


@needs_db
@pytest.mark.asyncio
async def test_item_detail_has_owner(client):
    """Item detail should show the owner card."""
    browse = await client.get("/browse")
    match = re.search(r'href="/items/([^"]+)"', browse.text)
    resp = await client.get(f"/items/{match.group(1)}")
    assert "Listed by" in resp.text


@needs_db
@pytest.mark.asyncio
async def test_item_detail_404_nonexistent(client):
    """Item detail should return 404 for nonexistent slug."""
    resp = await client.get("/items/this-item-does-not-exist-12345")
    assert resp.status_code == 404


@needs_db
@pytest.mark.asyncio
async def test_item_detail_has_similar_items_section(client):
    """Item detail should have a Similar Items section."""
    browse = await client.get("/browse")
    match = re.search(r'href="/items/([^"]+)"', browse.text)
    resp = await client.get(f"/items/{match.group(1)}")
    assert "Similar Items" in resp.text or "similar_items" in resp.text


# --- Workshop Page ---

@needs_db
@pytest.mark.asyncio
async def test_workshop_returns_200(client):
    """Workshop page should return 200 for a valid slug."""
    resp = await client.get("/workshop/sallys-kitchen")
    assert resp.status_code == 200


@needs_db
@pytest.mark.asyncio
async def test_workshop_has_name(client):
    """Workshop page should show the workshop name."""
    resp = await client.get("/workshop/sallys-kitchen")
    assert "Sally" in resp.text


@needs_db
@pytest.mark.asyncio
async def test_workshop_404_nonexistent(client):
    """Workshop page should return 404 for nonexistent slug."""
    resp = await client.get("/workshop/nonexistent-workshop-12345")
    assert resp.status_code == 404
