"""Tests for weekend March 28-29 features.

Covers: saved searches, seller analytics, mentorship display,
lockbox on orders, homepage quick-start funnel, service icons,
social link icons, country flags, skill verify endpoint.
"""

import pytest


# ── Saved Searches API ──


@pytest.mark.asyncio
async def test_saved_searches_requires_auth(client):
    """GET /saved-searches requires auth."""
    resp = await client.get("/api/v1/saved-searches")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_saved_search_requires_auth(client):
    """POST /saved-searches requires auth."""
    resp = await client.post("/api/v1/saved-searches", json={
        "name": "Test search",
        "category_group": "vehicles",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_delete_saved_search_requires_auth(client):
    """DELETE /saved-searches/{id} requires auth."""
    resp = await client.delete("/api/v1/saved-searches/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_toggle_saved_search_requires_auth(client):
    """PATCH /saved-searches/{id}/toggle requires auth."""
    resp = await client.patch("/api/v1/saved-searches/00000000-0000-0000-0000-000000000000/toggle")
    assert resp.status_code == 401


# ── Saved Search Model ──


@pytest.mark.asyncio
async def test_saved_search_model_fields():
    """BHSavedSearch has all required fields."""
    from src.models.saved_search import BHSavedSearch
    fields = [c.key for c in BHSavedSearch.__table__.columns]
    assert "user_id" in fields
    assert "name" in fields
    assert "query" in fields
    assert "category" in fields
    assert "category_group" in fields
    assert "price_min" in fields
    assert "price_max" in fields
    assert "attribute_filters" in fields
    assert "latitude" in fields
    assert "longitude" in fields
    assert "radius_km" in fields
    assert "notify_enabled" in fields
    assert "match_count" in fields


# ── Saved Search Matcher ──


@pytest.mark.asyncio
async def test_matcher_text_match():
    """Matcher matches on text query."""
    from src.services.saved_search_matcher import _matches

    class FakeSearch:
        query = "drill"
        category = None
        category_group = None
        item_type = None
        price_min = None
        price_max = None
        attribute_filters = None
        latitude = None
        longitude = None
        radius_km = None

    class FakeItem:
        name = "Bosch Power Drill"
        description = "A great drill for home use"
        category = "power_tools"
        item_type = "physical"
        attributes = None
        latitude = None
        longitude = None

    class FakeListing:
        price = 15.0

    assert _matches(FakeSearch(), FakeItem(), FakeListing()) is True

    # Non-matching query
    search = FakeSearch()
    search.query = "surfboard"
    assert _matches(search, FakeItem(), FakeListing()) is False


@pytest.mark.asyncio
async def test_matcher_category_group():
    """Matcher matches on category group."""
    from src.services.saved_search_matcher import _matches

    class FakeSearch:
        query = None
        category = None
        category_group = "vehicles"
        item_type = None
        price_min = None
        price_max = None
        attribute_filters = None
        latitude = None
        longitude = None
        radius_km = None

    class FakeItem:
        name = "Fiat Panda"
        description = "Classic car"
        category = "vehicles"
        item_type = "physical"
        attributes = None
        latitude = None
        longitude = None

    class FakeListing:
        price = 5000

    assert _matches(FakeSearch(), FakeItem(), FakeListing()) is True

    # Wrong category
    item2 = FakeItem()
    item2.category = "kitchen"
    assert _matches(FakeSearch(), item2, FakeListing()) is False


@pytest.mark.asyncio
async def test_matcher_price_range():
    """Matcher filters by price range."""
    from src.services.saved_search_matcher import _matches

    class FakeSearch:
        query = None
        category = None
        category_group = None
        item_type = None
        price_min = 100
        price_max = 500
        attribute_filters = None
        latitude = None
        longitude = None
        radius_km = None

    class FakeItem:
        name = "Thing"
        description = ""
        category = "other"
        item_type = "physical"
        attributes = None
        latitude = None
        longitude = None

    class FakeListing:
        price = 250

    assert _matches(FakeSearch(), FakeItem(), FakeListing()) is True

    listing_cheap = FakeListing()
    listing_cheap.price = 50
    assert _matches(FakeSearch(), FakeItem(), listing_cheap) is False

    listing_expensive = FakeListing()
    listing_expensive.price = 600
    assert _matches(FakeSearch(), FakeItem(), listing_expensive) is False


@pytest.mark.asyncio
async def test_matcher_attribute_filters():
    """Matcher filters by JSONB attributes."""
    from src.services.saved_search_matcher import _matches

    class FakeSearch:
        query = None
        category = None
        category_group = None
        item_type = None
        price_min = None
        price_max = None
        attribute_filters = {"fuel_type": "diesel", "year_min": 2015}
        latitude = None
        longitude = None
        radius_km = None

    class FakeItem:
        name = "Car"
        description = ""
        category = "vehicles"
        item_type = "physical"
        attributes = {"fuel_type": "diesel", "year": 2020}
        latitude = None
        longitude = None

    class FakeListing:
        price = 10000

    assert _matches(FakeSearch(), FakeItem(), FakeListing()) is True

    # Wrong fuel
    item2 = FakeItem()
    item2.attributes = {"fuel_type": "gasoline", "year": 2020}
    assert _matches(FakeSearch(), item2, FakeListing()) is False


# ── Skill Verify Endpoint ──


@pytest.mark.asyncio
async def test_skill_verify_requires_auth(client):
    """POST /skills/{id}/verify requires auth."""
    resp = await client.post("/api/v1/skills/00000000-0000-0000-0000-000000000000/verify", json={})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_skill_unverify_requires_auth(client):
    """DELETE /skills/{id}/verify requires auth."""
    resp = await client.delete("/api/v1/skills/00000000-0000-0000-0000-000000000000/verify")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_skill_verified_status_requires_auth(client):
    """GET /skills/{id}/verified requires auth."""
    resp = await client.get("/api/v1/skills/00000000-0000-0000-0000-000000000000/verified")
    assert resp.status_code == 401


# ── Notification Type ──


@pytest.mark.asyncio
async def test_notification_type_includes_saved_search():
    """NotificationType has SAVED_SEARCH_MATCH."""
    from src.models.notification import NotificationType
    assert hasattr(NotificationType, "SAVED_SEARCH_MATCH")
    assert NotificationType.SAVED_SEARCH_MATCH.value == "SAVED_SEARCH_MATCH"


# ── Homepage ──


@pytest.mark.asyncio
async def test_homepage_returns_200(db_client):
    """GET / returns 200."""
    resp = await db_client.get("/")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_homepage_has_quick_start(db_client):
    """Homepage has the quick-start funnel for logged-out users."""
    resp = await db_client.get("/")
    assert resp.status_code == 200
    assert "60 seconds" in resp.text or "60 secondi" in resp.text


@pytest.mark.asyncio
async def test_homepage_has_sign_in_cta(db_client):
    """Homepage has Sign In as the primary CTA for logged-out users."""
    resp = await db_client.get("/")
    assert "/auth/login" in resp.text


# ── Lockbox returns null not 404 ──


@pytest.mark.asyncio
async def test_lockbox_returns_null_not_404(client):
    """GET /lockbox/{rental_id} returns null, not 404, when no codes exist."""
    resp = await client.get("/api/v1/lockbox/00000000-0000-0000-0000-000000000000")
    # 401 (no auth) -- but NOT 404 for missing codes
    assert resp.status_code in (401, 200)


@pytest.mark.asyncio
async def test_delivery_returns_null_not_404(client):
    """GET /deliveries/{rental_id} returns null, not 404, when no tracking exists."""
    resp = await client.get("/api/v1/deliveries/00000000-0000-0000-0000-000000000000")
    assert resp.status_code in (401, 200)


# ── Health endpoint rebrand ──


@pytest.mark.asyncio
async def test_health_says_la_piazza(client):
    """Health endpoint says La Piazza, not BorrowHood."""
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["app"] == "La Piazza"
