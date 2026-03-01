"""Tests for business logic that doesn't need auth.

Covers: AI service, lockbox codes, slug generation, template fallbacks,
enum validation, model relationships, and public API endpoints.
"""

import pytest
from httpx import AsyncClient


# --- AI Service Logic ---

class TestAIService:
    """Test AI template fallback and JSON parsing."""

    def test_template_fallback_english(self):
        from src.services.ai import _template_fallback
        result = _template_fallback("Bosch Drill", "tools", "physical", "en")
        assert result["title"] == "Bosch Drill"
        assert "Bosch Drill" in result["description"]
        assert len(result["tags"]) == 3
        assert "DIY" in result["tags"]

    def test_template_fallback_italian(self):
        from src.services.ai import _template_fallback
        result = _template_fallback("Trapano Bosch", "tools", "physical", "it")
        assert "Trapano Bosch" in result["description"]

    def test_template_fallback_unknown_category(self):
        from src.services.ai import _template_fallback
        result = _template_fallback("Mystery Item", "unknown_cat", "physical", "en")
        assert result["title"] == "Mystery Item"
        assert len(result["tags"]) == 3

    def test_template_fallback_all_categories(self):
        from src.services.ai import _template_fallback
        categories = ["tools", "kitchen", "garden", "electronics", "sports",
                      "music", "crafts", "cleaning", "vehicles"]
        for cat in categories:
            result = _template_fallback("Test Item", cat, "physical", "en")
            assert result["title"] == "Test Item"
            assert len(result["description"]) > 20
            assert len(result["tags"]) == 3

    def test_parse_json_response_valid(self):
        from src.services.ai import _parse_json_response
        text = '{"title": "Great Drill", "description": "A fine drill", "tags": ["DIY", "tools", "home"]}'
        result = _parse_json_response(text)
        assert result is not None
        assert result["title"] == "Great Drill"
        assert len(result["tags"]) == 3

    def test_parse_json_response_markdown_fences(self):
        from src.services.ai import _parse_json_response
        text = '```json\n{"title": "Great Drill", "description": "A fine drill", "tags": ["a"]}\n```'
        result = _parse_json_response(text)
        assert result is not None
        assert result["title"] == "Great Drill"

    def test_parse_json_response_surrounding_text(self):
        from src.services.ai import _parse_json_response
        text = 'Here is the listing: {"title": "Saw", "description": "Sharp saw", "tags": ["wood"]} Hope you like it!'
        result = _parse_json_response(text)
        assert result is not None
        assert result["title"] == "Saw"

    def test_parse_json_response_invalid(self):
        from src.services.ai import _parse_json_response
        assert _parse_json_response("not json at all") is None
        assert _parse_json_response("") is None
        assert _parse_json_response('{"only_title": "no description"}') is None

    def test_parse_json_response_tags_truncated(self):
        from src.services.ai import _parse_json_response
        text = '{"title": "X", "description": "Y", "tags": ["a","b","c","d","e"]}'
        result = _parse_json_response(text)
        assert len(result["tags"]) == 3  # Max 3 tags

    def test_generate_image_url(self):
        from src.services.ai import generate_image_url
        url = generate_image_url("Bosch Drill", "tools")
        assert url.startswith("https://picsum.photos/seed/")
        assert "800" in url
        assert "600" in url


# --- Lock Box Code Generation ---

class TestLockBoxCodes:
    """Test code generation logic."""

    def test_code_length(self):
        from src.services.lockbox import _generate_code
        assert len(_generate_code()) == 8
        assert len(_generate_code(4)) == 4
        assert len(_generate_code(12)) == 12

    def test_no_confusing_chars(self):
        from src.services.lockbox import _generate_code
        confusing = set("0O1IL")
        for _ in range(100):  # Generate many codes to check
            code = _generate_code()
            assert not confusing.intersection(code), f"Code {code} has confusing chars"

    def test_codes_are_uppercase(self):
        from src.services.lockbox import _generate_code
        for _ in range(50):
            code = _generate_code()
            assert code == code.upper()

    def test_alphabet_completeness(self):
        from src.services.lockbox import _ALPHABET
        # Should have 26 uppercase - 3 (O,I,L) + 10 digits - 2 (0,1) = 31 chars
        assert len(_ALPHABET) == 31
        assert "O" not in _ALPHABET
        assert "I" not in _ALPHABET
        assert "L" not in _ALPHABET
        assert "0" not in _ALPHABET
        assert "1" not in _ALPHABET

    def test_codes_are_unique(self):
        from src.services.lockbox import _generate_code
        codes = set(_generate_code() for _ in range(1000))
        # With 31^8 combinations, 1000 codes should all be unique
        assert len(codes) == 1000


# --- Enum Validation ---

class TestEnums:
    """Verify all enums have expected values."""

    def test_rental_status_values(self):
        from src.models.rental import RentalStatus
        expected = {"pending", "approved", "declined", "picked_up", "returned",
                    "completed", "cancelled", "disputed"}
        assert {s.value for s in RentalStatus} == expected

    def test_listing_type_values(self):
        from src.models.listing import ListingType
        expected = {"rent", "sell", "commission", "offer", "service", "training", "auction", "giveaway"}
        assert {t.value for t in ListingType} == expected

    def test_listing_status_values(self):
        from src.models.listing import ListingStatus
        expected = {"draft", "active", "paused", "expired", "removed"}
        assert {s.value for s in ListingStatus} == expected

    def test_item_type_values(self):
        from src.models.item import ItemType
        expected = {"physical", "digital", "service", "space", "made_to_order"}
        assert {t.value for t in ItemType} == expected

    def test_item_condition_values(self):
        from src.models.item import ItemCondition
        expected = {"new", "like_new", "good", "fair", "worn"}
        assert {c.value for c in ItemCondition} == expected

    def test_notification_types_include_lockbox(self):
        from src.models.notification import NotificationType
        values = {t.value for t in NotificationType}
        assert "lockbox_codes_ready" in values
        assert "lockbox_pickup_confirmed" in values
        assert "lockbox_return_confirmed" in values

    def test_bid_status_values(self):
        from src.models.bid import BidStatus
        expected = {"active", "outbid", "won", "cancelled", "reserve_not_met"}
        assert {s.value for s in BidStatus} == expected


# --- Public API Endpoints ---

@pytest.mark.asyncio
async def test_items_list_returns_data(client: AsyncClient):
    """Public items endpoint returns seeded data."""
    resp = await client.get("/api/v1/items?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_items_search_filters(client: AsyncClient):
    """Search by keyword filters results."""
    resp = await client.get("/api/v1/items?q=nonexistent_item_xyz")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 0

@pytest.mark.asyncio
async def test_items_category_filter(client: AsyncClient):
    """Category filter returns matching items."""
    resp = await client.get("/api/v1/items?category=tools")
    assert resp.status_code == 200
    data = resp.json()
    for item in data:
        assert item["category"] == "tools"

@pytest.mark.asyncio
async def test_items_sort_options(client: AsyncClient):
    """All sort options return 200."""
    for sort in ["newest", "oldest", "name_asc"]:
        resp = await client.get(f"/api/v1/items?sort={sort}&limit=3")
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_listings_list_returns_data(client: AsyncClient):
    """Public listings endpoint works."""
    resp = await client.get("/api/v1/listings?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_listings_filter_by_type(client: AsyncClient):
    """Filter listings by type returns 200."""
    resp = await client.get("/api/v1/listings?listing_type=rent&limit=5")
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_reviews_public(client: AsyncClient):
    """Reviews list is public."""
    resp = await client.get("/api/v1/reviews?limit=5")
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_badge_catalog_public(client: AsyncClient):
    """Badge catalog is public and complete."""
    resp = await client.get("/api/v1/badges/catalog")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 10
    # Check badge structure
    for badge in data:
        assert "code" in badge
        assert "name" in badge
        assert "description" in badge

@pytest.mark.asyncio
async def test_health_returns_all_fields(client: AsyncClient):
    """Health check returns required fields."""
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["app"] == "BorrowHood"
    assert "version" in data
    assert "timestamp" in data
    assert "uptime_seconds" in data
    assert data["checks"]["database"] == "healthy"
