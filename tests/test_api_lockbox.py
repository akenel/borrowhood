"""Tests for lock box access code API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_lockbox_generate_requires_auth(client: AsyncClient):
    """Generating codes requires authentication."""
    import uuid
    fake_id = str(uuid.uuid4())
    resp = await client.post(f"/api/v1/lockbox/{fake_id}/generate", json={})
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_lockbox_get_requires_auth(client: AsyncClient):
    """Getting codes requires authentication."""
    import uuid
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/v1/lockbox/{fake_id}")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_lockbox_verify_requires_auth(client: AsyncClient):
    """Verifying codes requires authentication."""
    import uuid
    fake_id = str(uuid.uuid4())
    resp = await client.post(f"/api/v1/lockbox/{fake_id}/verify", json={"code": "ABCD1234"})
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_lockbox_code_generation_logic():
    """Test the code generation service produces valid codes."""
    from src.services.lockbox import _generate_code, _ALPHABET

    code = _generate_code()
    assert len(code) == 8
    assert all(c in _ALPHABET for c in code)

    # No confusing characters
    for c in "0O1IL":
        assert c not in code

    # Two codes should be different (astronomically unlikely to be the same)
    code2 = _generate_code()
    assert code != code2


@pytest.mark.asyncio
async def test_lockbox_code_generation_custom_length():
    """Test custom code length."""
    from src.services.lockbox import _generate_code

    code = _generate_code(length=4)
    assert len(code) == 4

    code = _generate_code(length=12)
    assert len(code) == 12
