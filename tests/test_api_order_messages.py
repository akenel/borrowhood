"""Tests for BL-077: per-order messaging.

Verifies:
1. GET /api/v1/messages/order/{rental_id} returns messages for a transaction
2. Only renter and item owner can access order messages
3. Sending a message with rental_id validates authorization
4. ThreadSummary includes rental_id
"""

import asyncio
import logging
from uuid import UUID

import httpx
import pytest

logger = logging.getLogger(__name__)

BASE = "https://borrowhood.duckdns.org"


async def login(client: httpx.AsyncClient, username: str) -> dict:
    """Login and return user info."""
    resp = await client.post(
        f"{BASE}/api/v1/demo/login",
        json={"username": username, "password": "helix_pass"},
    )
    assert resp.status_code == 200, f"Login failed for {username}: {resp.text}"
    return resp.json()


async def get_my_id(client: httpx.AsyncClient) -> str:
    """Get current user's ID from threads endpoint (any API that returns user context)."""
    resp = await client.get(f"{BASE}/api/v1/users/me")
    assert resp.status_code == 200
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_order_thread_endpoint_exists():
    """GET /api/v1/messages/order/{rental_id} should return 401 without auth."""
    async with httpx.AsyncClient(verify=False, timeout=30.0) as client:
        resp = await client.get(f"{BASE}/api/v1/messages/order/00000000-0000-0000-0000-000000000000")
        assert resp.status_code in (401, 403), f"Expected auth error, got {resp.status_code}"


@pytest.mark.asyncio
async def test_order_thread_not_found():
    """GET /api/v1/messages/order/{bad_id} should return 404."""
    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=30.0) as client:
        await login(client, "mike")
        resp = await client.get(f"{BASE}/api/v1/messages/order/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404


@pytest.mark.asyncio
async def test_order_thread_returns_messages():
    """If a rental has messages, they should be returned in order."""
    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=30.0) as client:
        await login(client, "sally")

        # Find a rental where sally is the owner (has rentals on her items)
        resp = await client.get(f"{BASE}/api/v1/rentals?role=owner&limit=5")
        if resp.status_code != 200 or not resp.json():
            pytest.skip("No rentals found for sally as owner")

        rental = resp.json()[0]
        rental_id = rental["id"]

        # Try to get the order thread (may be empty, but should return 200)
        resp = await client.get(f"{BASE}/api/v1/messages/order/{rental_id}")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)
        logger.info("Order thread for rental %s: %d messages", rental_id[:8], len(resp.json()))


@pytest.mark.asyncio
async def test_send_message_with_rental_id():
    """Sending a message with rental_id should succeed for authorized users."""
    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=30.0) as client:
        # Login as john (renter)
        await login(client, "john")

        # Find a rental where john is the renter
        resp = await client.get(f"{BASE}/api/v1/rentals?role=renter&limit=5")
        if resp.status_code != 200 or not resp.json():
            pytest.skip("No rentals found for john as renter")

        rental = resp.json()[0]
        rental_id = rental["id"]
        listing_id = rental.get("listing_id")

        # Get the listing to find the owner
        if listing_id:
            listing_resp = await client.get(f"{BASE}/api/v1/listings/{listing_id}")
            if listing_resp.status_code == 200:
                item_id = listing_resp.json().get("item_id")
                if item_id:
                    item_resp = await client.get(f"{BASE}/api/v1/items/{item_id}")
                    if item_resp.status_code == 200:
                        owner_id = item_resp.json().get("owner_id")

                        # Send a message tied to this rental
                        msg_resp = await client.post(
                            f"{BASE}/api/v1/messages",
                            json={
                                "recipient_id": owner_id,
                                "body": "Test message for order thread (BL-077 test)",
                                "rental_id": rental_id,
                                "listing_id": listing_id,
                            },
                        )
                        assert msg_resp.status_code == 201, f"Send failed: {msg_resp.text}"
                        msg_data = msg_resp.json()
                        assert msg_data["rental_id"] == rental_id
                        logger.info("Sent message with rental_id=%s", rental_id[:8])

                        # Now verify it shows up in the order thread
                        thread_resp = await client.get(f"{BASE}/api/v1/messages/order/{rental_id}")
                        assert thread_resp.status_code == 200
                        messages = thread_resp.json()
                        assert any(m["body"] == "Test message for order thread (BL-077 test)" for m in messages)
                        logger.info("Message found in order thread")

                        # Clean up: delete the test message
                        await client.delete(f"{BASE}/api/v1/messages/{msg_data['id']}")
                        return

        pytest.skip("Could not resolve rental -> listing -> item -> owner chain")


@pytest.mark.asyncio
async def test_unauthorized_user_cannot_access_order_thread():
    """A user who is not renter or owner should get 403."""
    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=30.0) as client:
        # Login as sally to find one of her rentals
        await login(client, "sally")
        resp = await client.get(f"{BASE}/api/v1/rentals?role=owner&limit=1")
        if resp.status_code != 200 or not resp.json():
            pytest.skip("No rentals found")
        rental_id = resp.json()[0]["id"]

        # Now login as nino (not involved in this rental)
        await login(client, "nino")
        resp = await client.get(f"{BASE}/api/v1/messages/order/{rental_id}")
        assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
        logger.info("Unauthorized access correctly blocked")


@pytest.mark.asyncio
async def test_thread_summary_includes_rental_id():
    """ThreadSummary should include rental_id field."""
    async with httpx.AsyncClient(verify=False, follow_redirects=True, timeout=30.0) as client:
        await login(client, "john")
        resp = await client.get(f"{BASE}/api/v1/messages/threads")
        assert resp.status_code == 200
        threads = resp.json()
        if threads:
            # Verify the schema has rental_id (even if null)
            assert "rental_id" in threads[0], "ThreadSummary missing rental_id field"
            logger.info("ThreadSummary includes rental_id: %s", threads[0].get("rental_id"))
