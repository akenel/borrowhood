"""Payment API tests."""

import pytest


@pytest.mark.asyncio
async def test_create_order_requires_auth(client):
    """POST /api/v1/payments/create-order should require auth."""
    resp = await client.post("/api/v1/payments/create-order", json={
        "rental_id": "00000000-0000-0000-0000-000000000001",
        "payment_type": "rental",
        "amount": 25.0,
    })
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_capture_requires_auth(client):
    """POST /api/v1/payments/capture should require auth."""
    resp = await client.post("/api/v1/payments/capture", json={
        "payment_id": "00000000-0000-0000-0000-000000000001",
        "paypal_order_id": "FAKE123",
    })
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_refund_requires_auth(client):
    """POST /api/v1/payments/{id}/refund should require auth."""
    fake_id = "00000000-0000-0000-0000-000000000001"
    resp = await client.post(f"/api/v1/payments/{fake_id}/refund", json={})
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_payments_requires_auth(client):
    """GET /api/v1/payments should require auth."""
    resp = await client.get("/api/v1/payments")
    assert resp.status_code in (401, 403)
