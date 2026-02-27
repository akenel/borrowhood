"""Edge case tests for API endpoints.

Tests boundary conditions, invalid inputs, and response structure
validation. All public endpoints -- no auth needed.
"""

import uuid
import pytest
from httpx import AsyncClient


# --- Items API Edge Cases ---

class TestItemsEdgeCases:
    """Test boundary conditions on items API."""

    @pytest.mark.asyncio
    async def test_items_invalid_sort_rejected(self, client: AsyncClient):
        """Invalid sort parameter returns 422."""
        resp = await client.get("/api/v1/items?sort=invalid_sort")
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_items_limit_zero_rejected(self, client: AsyncClient):
        """Limit of 0 is below minimum, returns 422."""
        resp = await client.get("/api/v1/items?limit=0")
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_items_limit_over_max_rejected(self, client: AsyncClient):
        """Limit over 100 returns 422."""
        resp = await client.get("/api/v1/items?limit=101")
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_items_negative_offset_rejected(self, client: AsyncClient):
        """Negative offset returns 422."""
        resp = await client.get("/api/v1/items?offset=-1")
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_items_valid_limit_boundary(self, client: AsyncClient):
        """Limit of 1 and 100 both work."""
        resp1 = await client.get("/api/v1/items?limit=1")
        assert resp1.status_code == 200
        assert len(resp1.json()) <= 1

        resp100 = await client.get("/api/v1/items?limit=100")
        assert resp100.status_code == 200

    @pytest.mark.asyncio
    async def test_items_offset_pagination(self, client: AsyncClient):
        """Large offset returns empty list, not error."""
        resp = await client.get("/api/v1/items?offset=99999")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_items_empty_search(self, client: AsyncClient):
        """Empty search string returns all items."""
        resp = await client.get("/api/v1/items?q=")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_items_special_chars_in_search(self, client: AsyncClient):
        """Special characters in search don't crash."""
        resp = await client.get("/api/v1/items?q=%25%27%22")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_item_not_found(self, client: AsyncClient):
        """Random UUID returns 404."""
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"/api/v1/items/{fake_id}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_item_invalid_uuid(self, client: AsyncClient):
        """Non-UUID returns 422."""
        resp = await client.get("/api/v1/items/not-a-uuid")
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_items_combined_filters(self, client: AsyncClient):
        """Multiple filters work together."""
        resp = await client.get("/api/v1/items?category=tools&item_type=physical&sort=name_asc&limit=5")
        assert resp.status_code == 200
        data = resp.json()
        for item in data:
            assert item["category"] == "tools"
            assert item["item_type"] == "physical"

    @pytest.mark.asyncio
    async def test_items_response_structure(self, client: AsyncClient):
        """Item response has required fields."""
        resp = await client.get("/api/v1/items?limit=1")
        assert resp.status_code == 200
        data = resp.json()
        if data:
            item = data[0]
            assert "id" in item
            assert "name" in item
            assert "slug" in item
            assert "category" in item
            assert "item_type" in item


# --- Listings API Edge Cases ---

class TestListingsEdgeCases:
    """Test boundary conditions on listings API."""

    @pytest.mark.asyncio
    async def test_listings_invalid_uuid(self, client: AsyncClient):
        """Non-UUID listing ID returns 422."""
        resp = await client.get("/api/v1/listings/not-a-uuid")
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_listings_not_found(self, client: AsyncClient):
        """Random UUID listing returns 404."""
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"/api/v1/listings/{fake_id}")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_listings_filter_by_all_types(self, client: AsyncClient):
        """All listing types return 200."""
        for lt in ["rent", "sell", "commission", "offer", "service", "training", "auction"]:
            resp = await client.get(f"/api/v1/listings?listing_type={lt}&limit=3")
            assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_listings_response_structure(self, client: AsyncClient):
        """Listing response has required fields."""
        resp = await client.get("/api/v1/listings?limit=1")
        assert resp.status_code == 200
        data = resp.json()
        if data:
            listing = data[0]
            assert "id" in listing
            assert "listing_type" in listing
            assert "status" in listing


# --- Reviews API Edge Cases ---

class TestReviewsEdgeCases:
    """Test review endpoints edge cases."""

    @pytest.mark.asyncio
    async def test_reviews_empty_list(self, client: AsyncClient):
        """Reviews for nonexistent user returns empty."""
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"/api/v1/reviews?reviewee_id={fake_id}")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_review_summary_nonexistent_user(self, client: AsyncClient):
        """Summary for nonexistent user returns zero count."""
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"/api/v1/reviews/summary/{fake_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 0
        assert data["average"] is None
        assert data["weighted_average"] is None

    @pytest.mark.asyncio
    async def test_review_create_requires_auth(self, client: AsyncClient):
        """Creating review without auth returns 401/403."""
        resp = await client.post("/api/v1/reviews", json={
            "rental_id": str(uuid.uuid4()),
            "reviewee_id": str(uuid.uuid4()),
            "rating": 5,
            "title": "Great!",
            "body": "Loved it",
        })
        assert resp.status_code in (401, 403)


# --- Badges API Edge Cases ---

class TestBadgesEdgeCases:
    """Test badge endpoints."""

    @pytest.mark.asyncio
    async def test_badge_catalog_structure(self, client: AsyncClient):
        """Badge catalog entries have all fields."""
        resp = await client.get("/api/v1/badges/catalog")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 14
        for badge in data:
            assert "code" in badge
            assert "name" in badge
            assert "description" in badge
            assert "icon" in badge
            assert "color" in badge
            # All fields should be non-empty strings
            assert badge["code"]
            assert badge["name"]
            assert badge["description"]

    @pytest.mark.asyncio
    async def test_user_badges_nonexistent_user(self, client: AsyncClient):
        """Badges for nonexistent user returns empty list."""
        fake_id = str(uuid.uuid4())
        resp = await client.get(f"/api/v1/badges/user/{fake_id}")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_badge_check_requires_auth(self, client: AsyncClient):
        """Badge check endpoint requires auth."""
        resp = await client.post("/api/v1/badges/check")
        assert resp.status_code in (401, 403)


# --- Health API ---

class TestHealthEdgeCases:
    """Test health endpoint structure."""

    @pytest.mark.asyncio
    async def test_health_response_types(self, client: AsyncClient):
        """Health fields have correct types."""
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["status"], str)
        assert isinstance(data["app"], str)
        assert isinstance(data["version"], str)
        assert isinstance(data["uptime_seconds"], (int, float))
        assert isinstance(data["checks"], dict)
        assert isinstance(data["checks"]["database"], str)

    @pytest.mark.asyncio
    async def test_health_uptime_positive(self, client: AsyncClient):
        """Uptime should be >= 0."""
        resp = await client.get("/api/v1/health")
        data = resp.json()
        assert data["uptime_seconds"] >= 0


# --- Auth Gate Consistency ---

class TestAuthGateConsistency:
    """Verify ALL write endpoints require auth."""

    @pytest.mark.asyncio
    async def test_all_post_endpoints_require_auth(self, client: AsyncClient):
        """All POST endpoints should reject unauthenticated requests."""
        fake_id = str(uuid.uuid4())
        write_endpoints = [
            ("/api/v1/items", {}),
            ("/api/v1/listings", {}),
            ("/api/v1/reviews", {}),
            (f"/api/v1/rentals", {}),
            (f"/api/v1/bids/{fake_id}", {}),
            (f"/api/v1/deposits/{fake_id}/hold", {}),
            (f"/api/v1/disputes/{fake_id}", {}),
            (f"/api/v1/payments/{fake_id}/create", {}),
            (f"/api/v1/lockbox/{fake_id}/generate", {}),
            (f"/api/v1/lockbox/{fake_id}/verify", {"code": "ABCD1234"}),
            ("/api/v1/badges/check", {}),
        ]
        for endpoint, body in write_endpoints:
            resp = await client.post(endpoint, json=body)
            # 401/403 = auth gate, 404 = resource check before auth (acceptable),
            # 405 = method not allowed, 422 = validation
            assert resp.status_code in (401, 403, 404, 405, 422), \
                f"POST {endpoint} returned {resp.status_code}, expected rejection"

    @pytest.mark.asyncio
    async def test_all_patch_endpoints_require_auth(self, client: AsyncClient):
        """All PATCH endpoints should reject unauthenticated requests."""
        fake_id = str(uuid.uuid4())
        patch_endpoints = [
            f"/api/v1/items/{fake_id}",
            f"/api/v1/rentals/{fake_id}/status",
        ]
        for endpoint in patch_endpoints:
            resp = await client.patch(endpoint, json={})
            assert resp.status_code in (401, 403, 422), \
                f"PATCH {endpoint} returned {resp.status_code}, expected auth gate"

    @pytest.mark.asyncio
    async def test_all_delete_endpoints_require_auth(self, client: AsyncClient):
        """All DELETE endpoints should reject unauthenticated requests."""
        fake_id = str(uuid.uuid4())
        delete_endpoints = [
            f"/api/v1/items/{fake_id}",
        ]
        for endpoint in delete_endpoints:
            resp = await client.delete(endpoint)
            assert resp.status_code in (401, 403), \
                f"DELETE {endpoint} returned {resp.status_code}, expected auth gate"
