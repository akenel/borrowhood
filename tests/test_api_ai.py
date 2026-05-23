"""Tests for AI generation endpoints."""

import asyncio
import sys
import time
from unittest.mock import patch, MagicMock

import pytest


@pytest.mark.asyncio
async def test_gemini_call_text_respects_timeout():
    """Task #29: the shared _gemini_call_text helper must time out and return
    None when Gemini is slow -- so all five LLM services (helpboard, skills,
    listing, review, concierge) get hang-protection in one place.

    Patches the Gemini client to sleep longer than the configured timeout
    and asserts the helper returns None within the timeout window.
    """
    from src.services.llm import _common as cm

    def slow_generate(**kwargs):
        time.sleep(2.0)  # blocking sleep -- runs in to_thread worker
        return MagicMock(text='ignored')

    mock_client = MagicMock()
    mock_client.models.generate_content = slow_generate

    with patch.object(cm, "_get_gemini_client", return_value=mock_client):
        start = time.monotonic()
        result = await cm._gemini_call_text("test prompt", timeout=0.2)
        elapsed = time.monotonic() - start

    assert result is None, "Slow Gemini call must return None, not block forever"
    assert elapsed < 1.0, (
        f"Gemini timeout did not fire — elapsed {elapsed:.2f}s "
        f"(should be ~0.2s for 0.2s timeout)"
    )


@pytest.mark.asyncio
async def test_gemini_call_text_returns_none_when_no_client():
    """No GOOGLE_API_KEY -> _get_gemini_client returns None -> helper returns
    None immediately without trying to call the SDK. Lets the cascade flow
    straight to Ollama / Pollinations / template.
    """
    from src.services.llm import _common as cm

    with patch.object(cm, "_get_gemini_client", return_value=None):
        result = await cm._gemini_call_text("test prompt")
    assert result is None


@pytest.mark.asyncio
async def test_all_five_llm_services_use_shared_gemini_helper():
    """Task #29 contract: every service that talks to Gemini must go through
    _gemini_call_text. If any service bypasses it (direct client call), it
    loses the timeout protection -- which is exactly the bug we fixed.

    Patches the shared helper to return None and asserts ALL FIVE services'
    gemini wrappers honor it (return None when helper returns None). Catches
    regressions where someone reintroduces a direct client.models.generate_content
    call without going through the helper.
    """
    from src.services.llm import helpboard, skills, listing, review, concierge

    cascade_targets = [
        ("helpboard",  helpboard._helpboard_draft_gemini),
        ("skills",     skills._skills_gemini),
        ("listing",    listing._smart_listing_gemini),
        ("review",     review._review_gemini),
        ("concierge",  concierge._concierge_gemini),
    ]

    # Patch the helper to return None — every service must respect this and
    # return None too (don't trust a None text from a hypothetical bypass path).
    with patch("src.services.llm._common._gemini_call_text", return_value=None):
        for name, fn in cascade_targets:
            # Also patch each module's own re-import of the helper since
            # `from ._common import _gemini_call_text` creates a module-local name.
            mod = sys.modules[fn.__module__]
            with patch.object(mod, "_gemini_call_text", return_value=None):
                result = await fn("test prompt")
                assert result is None, (
                    f"Service {name} ignored helper returning None — "
                    "it may be calling client.models.generate_content directly, "
                    "bypassing the shared timeout protection."
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
