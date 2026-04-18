"""Concierge search: conversational item/member finder.

Part of the AI service cascade: gemini -> ollama -> pollinations -> template fallback.
Extracted from the original gemini.py on 2026-04-18.
"""

from typing import Optional, List, Any
import json
import logging
import httpx

from src.config import settings

from ._common import (
    _get_settings,
    _get_gemini_client,
    _get_provider_order,
    _parse_json_from_text,
    _ollama_generate,
    _pollinations_generate,
)

logger = logging.getLogger(__name__)

# ── Concierge Search ─────────────────────────────────────────────────


def _build_concierge_prompt(
    query: str, language: str,
    items: list = None, members: list = None,
) -> str:
    """Build the concierge prompt used by all providers."""
    s = _get_settings()
    community = s.community_name

    items_text = "No matching items found."
    if items:
        items_text = "MATCHING ITEMS:\n"
        for item in items[:10]:
            items_text += (
                f"- {item.get('name', '?')} (category: {item.get('category', '?')}, "
                f"condition: {item.get('condition', '?')})\n"
            )

    members_text = ""
    if members:
        members_text = "\nMATCHING MEMBERS:\n"
        for m in members[:5]:
            langs = m.get("languages", [])
            lang_str = ", ".join(langs) if isinstance(langs, list) else str(langs)
            members_text += (
                f"- {m.get('display_name', '?')} ({m.get('badge_tier', '?')}, "
                f"languages: {lang_str})\n"
            )

    return f"""You are the AI Concierge for La Piazza, a neighborhood sharing platform
in {community}. A user searched for: "{query}"

{items_text}
{members_text}

Format a friendly, conversational response like a helpful neighbor (not a search engine).
For each result, explain WHY it matches what they asked for.
If no results, suggest broadening the search or trying a different category.
Language: {language}

Reply ONLY with this JSON:
{{
  "interpretation": "what you understood they need",
  "response": "friendly conversational response with results",
  "suggestions": ["follow-up suggestion 1", "follow-up suggestion 2"]
}}"""


async def _concierge_gemini(prompt: str) -> Optional[dict]:
    """Try Gemini for concierge search."""
    client = _get_gemini_client()
    if not client:
        return None
    try:
        response = client.models.generate_content(
            model=_get_settings().gemini_model,
            contents=prompt,
        )
        data = _parse_json_from_text(response.text)
        if data and "response" in data:
            return data
        logger.warning("Gemini concierge_search: invalid JSON response")
    except Exception as e:
        logger.warning("Gemini concierge_search failed: %s", e)
    return None


async def _concierge_ollama(prompt: str) -> Optional[dict]:
    """Try Ollama for concierge search."""
    text = await _ollama_generate(prompt, json_mode=True)
    if text:
        data = _parse_json_from_text(text)
        if data and "response" in data:
            return data
        logger.warning("Ollama concierge_search: invalid JSON response")
    return None


async def _concierge_pollinations(prompt: str) -> Optional[dict]:
    """Try Pollinations for concierge search."""
    text = await _pollinations_generate(prompt, json_mode=True)
    if text:
        data = _parse_json_from_text(text)
        if data and "response" in data:
            return data
        logger.warning("Pollinations concierge_search: invalid JSON response")
    return None


async def concierge_search(
    query: str,
    language: str = "en",
    items: list = None,
    members: list = None,
) -> tuple[Optional[dict], str]:
    """Natural language search using the AI provider cascade.

    Returns (search_data, provider_name) or (None, "none").
    """
    prompt = _build_concierge_prompt(query, language, items, members)

    providers = _get_provider_order()
    dispatch = {
        "gemini": _concierge_gemini,
        "ollama": _concierge_ollama,
        "pollinations": _concierge_pollinations,
    }

    for provider in providers:
        fn = dispatch.get(provider)
        if fn:
            result = await fn(prompt)
            if result:
                logger.info("concierge_search served by %s", provider)
                return result, provider

    return None, "none"



