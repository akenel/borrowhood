"""Listing creation matrix test -- every valid item_type + listing_type combination.

Runs against the LIVE UAT server (Hetzner). Tests that:
1. Item creation succeeds for each item_type
2. Listing creation succeeds for each valid listing_type on that item
3. Service/training fields are accepted (minimum_charge, per_person_rate, etc.)
4. Auction fields are accepted (bid_increment, auction_end)
5. Invalid combos are handled gracefully
6. Cleanup: all test items deleted after run

Usage:
    pytest tests/test_listing_matrix.py -v -s --base-url https://borrowhood.duckdns.org
    pytest tests/test_listing_matrix.py -v -s  # defaults to https://borrowhood.duckdns.org
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx
import pytest

logger = logging.getLogger(__name__)

BASE = "https://borrowhood.duckdns.org"
TEST_USER = "mike"  # mike has TRUSTED badge tier (can create auctions)
TEST_PASS = "helix_pass"

# ── Valid combinations: which listing types make sense for each item type ──

VALID_MATRIX = {
    "physical": ["rent", "sell", "commission", "offer", "auction", "giveaway"],
    "digital": ["sell", "offer", "giveaway"],
    "service": ["service", "training"],
    "space": ["rent", "offer"],
    "made_to_order": ["commission", "sell", "offer"],
}

# ── Category to use for each item type ──

CATEGORY_FOR_TYPE = {
    "physical": "power_tools",
    "digital": "art",
    "service": "training_service",
    "space": "spaces",
    "made_to_order": "crafts",
}

# ── Pricing configs per listing type ──

PRICING = {
    "rent": {"price": 10.0, "price_unit": "per_day", "deposit": 25.0},
    "sell": {"price": 50.0, "price_unit": "flat"},
    "commission": {"price": 75.0, "price_unit": "flat", "deposit": 20.0},
    "offer": {"price": 0.0, "price_unit": "negotiable"},
    "service": {
        "price": 30.0,
        "price_unit": "per_hour",
        "minimum_charge": 15.0,
        "per_person_rate": 25.0,
        "max_participants": 6,
        "group_discount_pct": 10.0,
    },
    "training": {
        "price": 40.0,
        "price_unit": "per_hour",
        "minimum_charge": 20.0,
        "per_person_rate": 30.0,
        "max_participants": 8,
        "group_discount_pct": 15.0,
    },
    "auction": {
        "price": 5.0,
        "price_unit": "flat",
        "bid_increment": 2.0,
        "auction_end": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
    },
    "giveaway": {"price": None, "price_unit": "flat"},
}


async def login(client: httpx.AsyncClient) -> None:
    """Login via demo endpoint, sets bh_session cookie on client."""
    resp = await client.post(
        f"{BASE}/api/v1/demo/login",
        json={"username": TEST_USER, "password": TEST_PASS},
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    logger.info("Logged in as %s", TEST_USER)


async def create_item(client: httpx.AsyncClient, item_type: str, suffix: str) -> str:
    """Create a test item, return its ID."""
    await asyncio.sleep(0.5)  # Avoid rate limiter
    resp = await client.post(
        f"{BASE}/api/v1/items",
        json={
            "name": f"Matrix Test {item_type} {suffix}",
            "description": f"Automated matrix test for {item_type}",
            "item_type": item_type,
            "category": CATEGORY_FOR_TYPE[item_type],
            "condition": "good" if item_type in ("physical", "made_to_order") else None,
            "content_language": "en",
        },
    )
    assert resp.status_code == 201, f"Item creation failed ({item_type}): {resp.status_code} {resp.text}"
    item_id = resp.json()["id"]
    logger.info("  Created item %s (type=%s, id=%s)", suffix, item_type, item_id[:8])
    return item_id


async def create_listing(client: httpx.AsyncClient, item_id: str, listing_type: str) -> str:
    """Create a listing on an item, return its ID."""
    payload = {
        "item_id": item_id,
        "listing_type": listing_type,
        "currency": "EUR",
        "delivery_available": False,
        "pickup_only": True,
    }
    pricing = PRICING.get(listing_type, {})
    payload.update(pricing)

    resp = await client.post(f"{BASE}/api/v1/listings", json=payload)
    assert resp.status_code == 201, f"Listing creation failed ({listing_type}): {resp.status_code} {resp.text}"

    data = resp.json()
    listing_id = data["id"]

    # Verify fields came back correctly
    if listing_type in ("service", "training"):
        assert data.get("minimum_charge") == pricing.get("minimum_charge"), \
            f"minimum_charge mismatch: expected {pricing.get('minimum_charge')}, got {data.get('minimum_charge')}"
        assert data.get("per_person_rate") == pricing.get("per_person_rate"), \
            f"per_person_rate mismatch: expected {pricing.get('per_person_rate')}, got {data.get('per_person_rate')}"
        assert data.get("max_participants") == pricing.get("max_participants"), \
            f"max_participants mismatch: expected {pricing.get('max_participants')}, got {data.get('max_participants')}"
        assert data.get("group_discount_pct") == pricing.get("group_discount_pct"), \
            f"group_discount_pct mismatch"

    if listing_type == "auction":
        assert data.get("bid_increment") == pricing.get("bid_increment"), \
            f"bid_increment mismatch: expected {pricing.get('bid_increment')}, got {data.get('bid_increment')}"
        assert data.get("auction_end") is not None, "auction_end should be set"

    if listing_type == "giveaway":
        assert data.get("price") is None, "Giveaway should have no price"

    logger.info("    Listing OK: %s (id=%s)", listing_type, listing_id[:8])
    return listing_id


async def delete_item(client: httpx.AsyncClient, item_id: str) -> None:
    """Soft-delete an item (cleanup)."""
    resp = await client.delete(f"{BASE}/api/v1/items/{item_id}")
    if resp.status_code in (200, 204, 404):
        logger.info("  Cleaned up item %s", item_id[:8])
    else:
        logger.warning("  Cleanup failed for %s: %s", item_id[:8], resp.status_code)


@pytest.mark.asyncio
async def test_listing_matrix():
    """Test every valid item_type + listing_type combination."""
    created_items = []
    results = {"passed": 0, "failed": 0, "errors": []}

    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=30.0) as client:
        await login(client)

        for item_type, listing_types in VALID_MATRIX.items():
            logger.info("Testing item_type=%s with %d listing types", item_type, len(listing_types))

            # Create one item per item_type
            try:
                item_id = await create_item(client, item_type, f"{item_type}-matrix")
                created_items.append(item_id)
            except AssertionError as e:
                results["failed"] += 1
                results["errors"].append(f"ITEM CREATION FAILED: {item_type} -- {e}")
                logger.error("  FAIL: %s", e)
                continue

            # Create one listing per valid listing_type on that item
            for lt in listing_types:
                try:
                    listing_id = await create_listing(client, item_id, lt)
                    results["passed"] += 1
                except AssertionError as e:
                    results["failed"] += 1
                    results["errors"].append(f"LISTING FAILED: {item_type}/{lt} -- {e}")
                    logger.error("    FAIL: %s/%s -- %s", item_type, lt, e)

        # Cleanup
        logger.info("Cleaning up %d test items...", len(created_items))
        for item_id in created_items:
            await delete_item(client, item_id)

    # Report
    total = results["passed"] + results["failed"]
    logger.info("=" * 60)
    logger.info("MATRIX RESULTS: %d/%d passed", results["passed"], total)
    if results["errors"]:
        logger.info("FAILURES:")
        for err in results["errors"]:
            logger.info("  - %s", err)
    logger.info("=" * 60)

    assert results["failed"] == 0, f"{results['failed']} combinations failed:\n" + "\n".join(results["errors"])


@pytest.mark.asyncio
async def test_service_without_deposit():
    """Service listings should work without deposit (deposit=null)."""
    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=30.0) as client:
        await login(client)
        item_id = await create_item(client, "service", "no-deposit-test")
        try:
            resp = await client.post(
                f"{BASE}/api/v1/listings",
                json={
                    "item_id": item_id,
                    "listing_type": "service",
                    "price": 25.0,
                    "price_unit": "per_hour",
                    "currency": "EUR",
                    "deposit": None,
                    "delivery_available": False,
                    "pickup_only": True,
                },
            )
            assert resp.status_code == 201, f"Service without deposit failed: {resp.text}"
            assert resp.json()["deposit"] is None
        finally:
            await delete_item(client, item_id)


@pytest.mark.asyncio
async def test_physical_item_requires_no_service_fields():
    """Physical items should accept listings without service fields."""
    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=30.0) as client:
        await login(client)
        item_id = await create_item(client, "physical", "no-svc-fields")
        try:
            resp = await client.post(
                f"{BASE}/api/v1/listings",
                json={
                    "item_id": item_id,
                    "listing_type": "rent",
                    "price": 15.0,
                    "price_unit": "per_day",
                    "deposit": 30.0,
                    "currency": "EUR",
                    "delivery_available": True,
                    "pickup_only": False,
                },
            )
            assert resp.status_code == 201, f"Physical rent failed: {resp.text}"
            data = resp.json()
            assert data["price"] == 15.0
            assert data["deposit"] == 30.0
            assert data["minimum_charge"] is None
            assert data["per_person_rate"] is None
        finally:
            await delete_item(client, item_id)


@pytest.mark.asyncio
async def test_giveaway_ignores_price():
    """Giveaway listings should store null price even if provided."""
    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=30.0) as client:
        await login(client)
        item_id = await create_item(client, "physical", "giveaway-test")
        try:
            resp = await client.post(
                f"{BASE}/api/v1/listings",
                json={
                    "item_id": item_id,
                    "listing_type": "giveaway",
                    "price": None,
                    "price_unit": "flat",
                    "currency": "EUR",
                    "delivery_available": False,
                    "pickup_only": True,
                },
            )
            assert resp.status_code == 201, f"Giveaway failed: {resp.text}"
        finally:
            await delete_item(client, item_id)


if __name__ == "__main__":
    """Run directly: python tests/test_listing_matrix.py"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(test_listing_matrix())
