"""Tests for AI generation endpoints."""

import asyncio
import time
from unittest.mock import patch, MagicMock

import pytest


@pytest.mark.asyncio
async def test_helpboard_gemini_call_respects_timeout():
    """BL-2: Gemini SDK call must time out + return None when slow, NOT hang.

    Patches the Gemini client to sleep longer than the configured timeout.
    The async wrapper (asyncio.wait_for + asyncio.to_thread) must cancel
    the await and return None within the timeout window so the cascade
    can fall through to Ollama / Pollinations / template fallback.
    """
    from src.services.llm import helpboard as hb_mod

    # Make the Gemini client's generate_content sleep longer than the timeout
    def slow_generate(**kwargs):
        time.sleep(2.0)  # blocking sleep -- runs in to_thread worker
        return MagicMock(text='{"title":"x","body":"x"}')

    mock_client = MagicMock()
    mock_client.models.generate_content = slow_generate

    with patch.object(hb_mod, "_get_gemini_client", return_value=mock_client), \
         patch.object(hb_mod, "_GEMINI_TIMEOUT_S", 0.2):
        start = time.monotonic()
        result = await hb_mod._helpboard_draft_gemini("test prompt")
        elapsed = time.monotonic() - start

    assert result is None, "Slow Gemini call must return None, not block forever"
    assert elapsed < 1.0, (
        f"Gemini timeout did not fire — elapsed {elapsed:.2f}s "
        f"(should be ~0.2s for 0.2s timeout)"
    )


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
