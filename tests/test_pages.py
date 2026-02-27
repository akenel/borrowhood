"""Page route tests -- all HTML pages must return 200 with correct content."""

import pytest


# --- Home Page ---

@pytest.mark.asyncio
async def test_home_returns_200(client):
    """Home page should return 200."""
    resp = await client.get("/")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_home_has_app_name(client):
    """Home page should contain the app name."""
    resp = await client.get("/")
    assert "BorrowHood" in resp.text


@pytest.mark.asyncio
async def test_home_has_hero_title_en(client):
    """Home page in English should show English hero title."""
    resp = await client.get("/")
    assert "Every Garage Becomes a Rental Shop" in resp.text


@pytest.mark.asyncio
async def test_home_has_hero_title_it(client):
    """Home page in Italian should show Italian hero title."""
    resp = await client.get("/?lang=it")
    assert "Ogni Garage Diventa un Negozio di Noleggio" in resp.text


@pytest.mark.asyncio
async def test_home_has_stats(client):
    """Home page should show listing and member counts."""
    resp = await client.get("/")
    assert "Active Listings" in resp.text
    assert "Members" in resp.text


@pytest.mark.asyncio
async def test_home_has_how_it_works(client):
    """Home page should show How It Works section."""
    resp = await client.get("/")
    assert "How It Works" in resp.text


@pytest.mark.asyncio
async def test_home_has_origin_story(client):
    """Home page should contain the origin story."""
    resp = await client.get("/")
    assert "hand-shovel landscaper" in resp.text


@pytest.mark.asyncio
async def test_home_sets_lang_cookie(client):
    """Switching language should set bh_lang cookie."""
    resp = await client.get("/?lang=it")
    # Check set-cookie header directly (httpx cookies jar may not capture all)
    set_cookie = resp.headers.get("set-cookie", "")
    assert "bh_lang=it" in set_cookie


# --- Browse Page ---

@pytest.mark.asyncio
async def test_browse_returns_200(client):
    """Browse page should return 200."""
    resp = await client.get("/browse")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_browse_has_search(client):
    """Browse page should have a search input."""
    resp = await client.get("/browse")
    assert 'name="q"' in resp.text


@pytest.mark.asyncio
async def test_browse_has_filters(client):
    """Browse page should have category and type filters."""
    resp = await client.get("/browse")
    assert 'name="category"' in resp.text
    assert 'name="item_type"' in resp.text
    assert 'name="sort"' in resp.text


@pytest.mark.asyncio
async def test_browse_shows_items(client):
    """Browse page should show item cards (requires seed data)."""
    resp = await client.get("/browse")
    assert '/items/' in resp.text


@pytest.mark.asyncio
async def test_browse_i18n_it(client):
    """Browse page in Italian should use Italian labels."""
    resp = await client.get("/browse?lang=it")
    assert "Esplora Oggetti" in resp.text
    assert "Cerca" in resp.text


@pytest.mark.asyncio
async def test_browse_search_filter(client):
    """Browse page search should filter results."""
    resp = await client.get("/browse?q=cookie")
    assert resp.status_code == 200
    # Should find Sally's cookie cutters
    assert "cookie" in resp.text.lower()


@pytest.mark.asyncio
async def test_browse_sort_oldest(client):
    """Browse page should accept sort parameter."""
    resp = await client.get("/browse?sort=oldest")
    assert resp.status_code == 200


# --- Item Detail Page ---

@pytest.mark.asyncio
async def test_item_detail_returns_200(client):
    """Item detail page should return 200 for a valid slug."""
    # First get a valid slug from browse
    browse = await client.get("/browse")
    # Extract first item link
    import re
    match = re.search(r'href="/items/([^"]+)"', browse.text)
    assert match, "No item links found on browse page"
    slug = match.group(1)

    resp = await client.get(f"/items/{slug}")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_item_detail_has_breadcrumb(client):
    """Item detail should have breadcrumb navigation."""
    browse = await client.get("/browse")
    import re
    match = re.search(r'href="/items/([^"]+)"', browse.text)
    slug = match.group(1)

    resp = await client.get(f"/items/{slug}")
    assert "Home" in resp.text
    assert "Browse" in resp.text


@pytest.mark.asyncio
async def test_item_detail_has_owner(client):
    """Item detail should show the owner card."""
    browse = await client.get("/browse")
    import re
    match = re.search(r'href="/items/([^"]+)"', browse.text)
    slug = match.group(1)

    resp = await client.get(f"/items/{slug}")
    assert "Listed by" in resp.text


@pytest.mark.asyncio
async def test_item_detail_404_nonexistent(client):
    """Item detail should return 404 for nonexistent slug."""
    resp = await client.get("/items/this-item-does-not-exist-12345")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_item_detail_404_has_i18n(client):
    """404 page should use i18n translations."""
    resp = await client.get("/items/nonexistent")
    assert "Page not found" in resp.text

    resp_it = await client.get("/items/nonexistent?lang=it")
    assert "Pagina non trovata" in resp_it.text


# --- Workshop Page ---

@pytest.mark.asyncio
async def test_workshop_returns_200(client):
    """Workshop page should return 200 for a valid slug."""
    resp = await client.get("/workshop/sallys-kitchen")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_workshop_has_name(client):
    """Workshop page should show the workshop name."""
    resp = await client.get("/workshop/sallys-kitchen")
    assert "Sally" in resp.text


@pytest.mark.asyncio
async def test_workshop_has_items(client):
    """Workshop page should show the owner's items."""
    resp = await client.get("/workshop/sallys-kitchen")
    assert "Items" in resp.text


@pytest.mark.asyncio
async def test_workshop_404_nonexistent(client):
    """Workshop page should return 404 for nonexistent slug."""
    resp = await client.get("/workshop/nonexistent-workshop-12345")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_workshop_i18n_it(client):
    """Workshop page in Italian should use Italian labels."""
    resp = await client.get("/workshop/sallys-kitchen?lang=it")
    assert "Chi Sono" in resp.text or "Oggetti" in resp.text
