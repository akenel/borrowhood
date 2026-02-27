"""Tests for AI generation endpoints."""

import pytest


@pytest.mark.asyncio
async def test_generate_listing_requires_auth(client):
    """AI listing generation requires authentication."""
    resp = await client.post("/api/v1/ai/generate-listing", json={
        "name": "Bosch Drill",
        "category": "tools",
    })
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_generate_skill_bio_requires_auth(client):
    """AI skill bio generation requires authentication."""
    resp = await client.post("/api/v1/ai/generate-skill-bio", json={
        "skill_input": "I know carpentry",
    })
    assert resp.status_code in (401, 403)


def test_template_fallback():
    """Template fallback generates reasonable descriptions."""
    from src.services.ai import _template_fallback

    result = _template_fallback("Bosch Drill", "tools", "physical", "en")
    assert "title" in result
    assert "description" in result
    assert "tags" in result
    assert len(result["tags"]) == 3
    assert "Bosch Drill" in result["description"]


def test_template_fallback_italian():
    """Template fallback works in Italian."""
    from src.services.ai import _template_fallback

    result = _template_fallback("Trapano Bosch", "tools", "physical", "it")
    assert "Trapano Bosch" in result["description"]


def test_parse_json_response():
    """JSON parsing handles various AI response formats."""
    from src.services.ai import _parse_json_response

    # Clean JSON
    result = _parse_json_response('{"title": "Test", "description": "A test", "tags": ["a", "b", "c"]}')
    assert result["title"] == "Test"
    assert len(result["tags"]) == 3

    # JSON with markdown fences
    result = _parse_json_response('```json\n{"title": "Test", "description": "A test", "tags": []}\n```')
    assert result["title"] == "Test"

    # JSON with surrounding text
    result = _parse_json_response('Here is the result: {"title": "Test", "description": "Desc"} hope this helps')
    assert result["title"] == "Test"

    # Invalid input
    assert _parse_json_response("not json at all") is None
    assert _parse_json_response('{"no_title": "missing"}') is None
