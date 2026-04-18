"""Smart listing generation (item name/description/tags/category).

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

def _build_listing_prompt(
    name: str, category: str, item_type: str, language: str,
    similar_items: list = None,
) -> str:
    """Build the listing prompt used by all providers."""
    s = _get_settings()
    community = s.community_name
    currency = s.community_currency

    similar_context = ""
    if similar_items:
        similar_context = "\n\nSIMILAR ITEMS ON THE PLATFORM (for price calibration):\n"
        for item in similar_items[:5]:
            similar_context += f"- {item.get('name', '?')}: {item.get('category', '?')}\n"

    categories_str = ", ".join(CATEGORIES)

    return f"""You are the Smart Listing Assistant for La Piazza, a neighborhood sharing platform
in {community}. Generate a complete listing from the item info below.

Item name: {name}
Category hint: {category or 'auto-detect'}
Item type: {item_type}
Language: {language}
{similar_context}

VALID CATEGORIES: {categories_str}

RULES:
- The Grandma Test: if an 83-year-old can't understand it, rewrite it.
- Prices should be fair for a neighborhood. {currency} 3-15/day for most tools.
- Write descriptions like a neighbor, not a salesperson.
- Match the user's language ({language}).

Reply ONLY with this JSON:
{{
  "title": "improved title",
  "description": "2-3 sentence warm description",
  "category": "valid_category",
  "subcategory": "more specific",
  "condition": "new|like_new|good|fair|worn",
  "item_type": "{item_type}",
  "suggested_price": 0.0,
  "price_unit": "per_day|per_hour|flat",
  "deposit_suggestion": 0.0,
  "suggested_listing_type": "rent|sell|auction|giveaway|commission|training|service",
  "tags": ["tag1", "tag2", "tag3"],
  "story_suggestion": "one sentence about the item character"
}}"""


async def _smart_listing_gemini(prompt: str) -> Optional[dict]:
    """Try Gemini for smart listing."""
    client = _get_gemini_client()
    if not client:
        return None
    try:
        response = client.models.generate_content(
            model=_get_settings().gemini_model,
            contents=prompt,
        )
        data = _parse_json_from_text(response.text)
        if data and "title" in data and "description" in data:
            return data
        logger.warning("Gemini smart_listing: invalid JSON response")
    except Exception as e:
        logger.warning("Gemini smart_listing failed: %s", e)
    return None


async def _smart_listing_ollama(prompt: str) -> Optional[dict]:
    """Try Ollama for smart listing."""
    text = await _ollama_generate(prompt, json_mode=True)
    if text:
        data = _parse_json_from_text(text)
        if data and "title" in data and "description" in data:
            return data
        logger.warning("Ollama smart_listing: invalid JSON response")
    return None


async def _smart_listing_pollinations(prompt: str) -> Optional[dict]:
    """Try Pollinations for smart listing."""
    text = await _pollinations_generate(prompt, json_mode=True)
    if text:
        data = _parse_json_from_text(text)
        if data and "title" in data and "description" in data:
            return data
        logger.warning("Pollinations smart_listing: invalid JSON response")
    return None


async def smart_listing(
    name: str,
    category: str = "",
    item_type: str = "physical",
    language: str = "en",
    similar_items: list = None,
) -> tuple[Optional[dict], str]:
    """Generate a complete listing using the AI provider cascade.

    Returns (listing_data, provider_name) or (None, "none").
    """
    prompt = _build_listing_prompt(name, category, item_type, language, similar_items)

    providers = _get_provider_order()
    dispatch = {
        "gemini": _smart_listing_gemini,
        "ollama": _smart_listing_ollama,
        "pollinations": _smart_listing_pollinations,
    }

    for provider in providers:
        fn = dispatch.get(provider)
        if fn:
            result = await fn(prompt)
            if result:
                # Validate category
                if result.get("category") not in CATEGORIES:
                    result["category"] = category or "hand_tools"
                logger.info("smart_listing served by %s", provider)
                return result, provider

    return None, "none"



