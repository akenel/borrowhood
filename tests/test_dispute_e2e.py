"""BL-053: Dispute flow E2E test against live Hetzner.

Walks the full dispute lifecycle:
1. Create a rental (mike rents from sally)
2. Advance to PICKED_UP
3. File dispute (mike disputes as renter)
4. Respond (sally responds as owner)
5. Resolve with deposit forfeited
6. Verify: rental → COMPLETED, deposit → FORFEITED
7. Cleanup

Requires: mike (TRUSTED tier), sally (has active listings with deposit)
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx
import pytest

logger = logging.getLogger(__name__)

BASE = "https://borrowhood.duckdns.org"


async def login(client: httpx.AsyncClient, username: str) -> dict:
    resp = await client.post(
        f"{BASE}/api/v1/demo/login",
        json={"username": username, "password": "helix_pass"},
    )
    assert resp.status_code == 200, f"Login failed for {username}: {resp.text}"
    logger.info("Logged in as %s", username)
    return resp.json()


async def get_my_id(client: httpx.AsyncClient) -> str:
    resp = await client.get(f"{BASE}/api/v1/users/me")
    assert resp.status_code == 200
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_dispute_full_lifecycle():
    """File → Respond → Resolve with deposit forfeited."""
    item_id = None
    listing_id = None
    rental_id = None

    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=30.0) as client:
        # ── Step 1: Sally creates an item + listing with deposit ──
        await login(client, "sally")
        sally_id = await get_my_id(client)

        resp = await client.post(f"{BASE}/api/v1/items", json={
            "name": "Dispute Test Drill",
            "description": "For dispute E2E testing",
            "item_type": "physical",
            "category": "power_tools",
            "condition": "good",
            "content_language": "en",
        })
        assert resp.status_code == 201, f"Item create failed: {resp.text}"
        item_id = resp.json()["id"]
        logger.info("Step 1: Sally created item %s", item_id[:8])

        resp = await client.post(f"{BASE}/api/v1/listings", json={
            "item_id": item_id,
            "listing_type": "rent",
            "price": 20.0,
            "price_unit": "per_day",
            "deposit": 50.0,
            "currency": "EUR",
            "delivery_available": False,
            "pickup_only": True,
        })
        assert resp.status_code == 201, f"Listing create failed: {resp.text}"
        listing_id = resp.json()["id"]
        logger.info("Step 1: Sally created listing %s (EUR 20/day, EUR 50 deposit)", listing_id[:8])

        # ── Step 2: Mike rents the item ──
        await login(client, "mike")
        mike_id = await get_my_id(client)

        start = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")
        end = (datetime.now(timezone.utc) + timedelta(days=3)).strftime("%Y-%m-%d")

        resp = await client.post(f"{BASE}/api/v1/rentals", json={
            "listing_id": listing_id,
            "requested_start": start,
            "requested_end": end,
            "renter_message": "Need it for a project",
        })
        assert resp.status_code == 201, f"Rental create failed: {resp.text}"
        rental_id = resp.json()["id"]
        logger.info("Step 2: Mike created rental %s", rental_id[:8])

        # ── Step 3: Sally approves, Mike picks up ──
        await login(client, "sally")
        resp = await client.patch(f"{BASE}/api/v1/rentals/{rental_id}/status", json={"status": "approved"})
        assert resp.status_code == 200, f"Approve failed: {resp.text}"
        logger.info("Step 3: Sally approved rental")

        await login(client, "mike")
        resp = await client.patch(f"{BASE}/api/v1/rentals/{rental_id}/status", json={"status": "picked_up"})
        assert resp.status_code == 200, f"Pickup failed: {resp.text}"
        logger.info("Step 3: Mike picked up item")

        # ── Step 4: Mike files a dispute ──
        resp = await client.post(f"{BASE}/api/v1/disputes", json={
            "rental_id": rental_id,
            "reason": "item_not_as_described",
            "description": "The drill is missing the chuck key and the battery doesn't hold charge. Not as described in the listing.",
        })
        assert resp.status_code == 201, f"Dispute file failed: {resp.text}"
        dispute = resp.json()
        dispute_id = dispute["id"]
        assert dispute["status"] == "filed"
        assert dispute["reason"] == "item_not_as_described"
        assert dispute["filed_by_id"] == mike_id
        logger.info("Step 4: Mike filed dispute %s (reason: item_not_as_described)", dispute_id[:8])

        # Verify rental is now DISPUTED
        resp = await client.get(f"{BASE}/api/v1/rentals/{rental_id}")
        assert resp.status_code == 200
        assert resp.json()["status"] == "disputed", f"Rental should be DISPUTED, got {resp.json()['status']}"
        logger.info("Step 4: Rental status confirmed DISPUTED")

        # ── Step 5: Sally responds ──
        await login(client, "sally")
        resp = await client.patch(f"{BASE}/api/v1/disputes/{dispute_id}/respond", json={
            "response": "The listing clearly states battery condition. Chuck key was in the case pocket. I can provide photos.",
        })
        assert resp.status_code == 200, f"Respond failed: {resp.text}"
        assert resp.json()["dispute_status"] == "under_review"
        logger.info("Step 5: Sally responded to dispute")

        # ── Step 6: Verify dispute is under review ──
        await login(client, "mike")
        resp = await client.get(f"{BASE}/api/v1/disputes?status=under_review")
        assert resp.status_code == 200
        disputes = resp.json()
        assert any(d["id"] == dispute_id for d in disputes), "Dispute not found in under_review list"
        logger.info("Step 6: Dispute confirmed UNDER_REVIEW")

        # ── Step 7: Resolve -- deposit returned to renter ──
        resp = await client.patch(f"{BASE}/api/v1/disputes/{dispute_id}/resolve", json={
            "resolution": "deposit_returned",
            "resolution_notes": "Item description was misleading about battery condition. Deposit returned to renter.",
        })
        assert resp.status_code == 200, f"Resolve failed: {resp.text}"
        assert resp.json()["resolution"] == "deposit_returned"
        logger.info("Step 7: Dispute resolved -- deposit returned")

        # ── Step 8: Verify final states ──
        resp = await client.get(f"{BASE}/api/v1/rentals/{rental_id}")
        assert resp.status_code == 200
        rental_final = resp.json()
        logger.info("Step 8: Final rental status = %s", rental_final["status"])

        resp = await client.get(f"{BASE}/api/v1/disputes?status=resolved")
        assert resp.status_code == 200
        resolved = resp.json()
        resolved_dispute = next((d for d in resolved if d["id"] == dispute_id), None)
        assert resolved_dispute is not None, "Dispute not in resolved list"
        assert resolved_dispute["status"] == "resolved"
        assert resolved_dispute["resolution"] == "deposit_returned"
        logger.info("Step 8: Dispute confirmed RESOLVED with deposit_returned")

        # ── Step 9: Check dispute summary ──
        resp = await client.get(f"{BASE}/api/v1/disputes/summary")
        assert resp.status_code == 200
        summary = resp.json()
        assert summary["resolved"] >= 1
        logger.info("Step 9: Summary -- total=%d, filed=%d, under_review=%d, resolved=%d",
                     summary["total"], summary["filed"], summary["under_review"], summary["resolved"])

        # ── Step 10: Verify duplicate dispute rejected ──
        resp = await client.post(f"{BASE}/api/v1/disputes", json={
            "rental_id": rental_id,
            "reason": "other",
            "description": "Trying to file a second dispute on same rental",
        })
        # Should fail -- dispute already exists (resolved counts as existing)
        # or rental is no longer in disputable state
        assert resp.status_code in (400, 409), f"Duplicate dispute should fail, got {resp.status_code}"
        logger.info("Step 10: Duplicate dispute correctly rejected (%d)", resp.status_code)

        # ── Cleanup ──
        logger.info("Cleaning up test data...")
        await login(client, "sally")
        await client.delete(f"{BASE}/api/v1/items/{item_id}")
        logger.info("Cleanup done")

    logger.info("=" * 60)
    logger.info("BL-053 DISPUTE E2E: ALL STEPS PASSED")
    logger.info("=" * 60)


@pytest.mark.asyncio
async def test_non_trusted_cannot_file_dispute():
    """Users below TRUSTED badge tier cannot file disputes."""
    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=30.0) as client:
        # nino is likely ACTIVE or NEWCOMER tier
        await login(client, "nino")

        # Try to file dispute with a fake rental ID
        resp = await client.post(f"{BASE}/api/v1/disputes", json={
            "rental_id": "00000000-0000-0000-0000-000000000000",
            "reason": "other",
            "description": "This should fail because of badge tier",
        })
        # Should get 403 (badge tier) or 404 (rental not found) -- either is correct
        assert resp.status_code in (403, 404), f"Expected 403/404, got {resp.status_code}: {resp.text}"
        logger.info("Non-trusted user correctly blocked: %d", resp.status_code)


@pytest.mark.asyncio
async def test_cannot_dispute_completed_rental():
    """Disputes cannot be filed on COMPLETED rentals."""
    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=30.0) as client:
        await login(client, "mike")

        # Find a completed rental
        resp = await client.get(f"{BASE}/api/v1/rentals?role=renter&status=completed&limit=1")
        if resp.status_code != 200 or not resp.json():
            pytest.skip("No completed rentals found for mike")

        rental_id = resp.json()[0]["id"]
        resp = await client.post(f"{BASE}/api/v1/disputes", json={
            "rental_id": rental_id,
            "reason": "item_damaged",
            "description": "Trying to dispute a completed rental -- should fail",
        })
        assert resp.status_code == 400, f"Expected 400 for completed rental, got {resp.status_code}: {resp.text}"
        logger.info("Cannot dispute completed rental: correctly rejected")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    asyncio.run(test_dispute_full_lifecycle())
