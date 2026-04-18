"""Help Board AI draft: turn a description into a clean post.

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

# ── Help Board AI Draft ──────────────────────────────────────────────


def _build_helpboard_prompt(description: str, help_type: str, language: str, similar_items: list = None) -> str:
    """Build prompt for AI-assisted help post drafting."""
    items_text = ""
    if similar_items:
        items_text = "\n\nSIMILAR ITEMS ON THE PLATFORM:\n"
        for item in similar_items[:5]:
            items_text += f"- {item['name']} (category: {item.get('category', '?')}, price: EUR {item.get('price', '?')}/day)\n"

    lang_instruction = f"Write the title and body in {language}." if language != "en" else ""

    return f"""You are the AI assistant for La Piazza, a community sharing platform.

A user wants to create a {"help request (I need help)" if help_type == "need" else "help offer (I can help)"} post.

Their short description: "{description}"
{items_text}
Your job:
1. Write a clear, friendly TITLE (max 200 chars) that tells the community what they need/offer
2. Write a BODY (2-4 paragraphs) that explains the situation, what they've tried, and what they need -- or what skills/tools they offer
3. Pick the best CATEGORY from: {', '.join(CATEGORIES)}
4. Set URGENCY: low, normal, or urgent
5. ESTIMATE the value of the item or service if relevant (what would it cost to buy/fix/replace?)
6. Explain WHY that value matters (so the user realizes giving things away or doing nothing has a cost)
7. Suggest 2-3 NEXT STEPS the user should consider before posting (like: check if someone on the platform already offers this, or: don't give it away -- ask for repair help first)

{lang_instruction}

Reply ONLY with this JSON:
{{{{
  "title": "...",
  "body": "...",
  "category": "...",
  "urgency": "normal",
  "estimated_value": 0.0,
  "value_explanation": "...",
  "suggestions": ["...", "...", "..."]
}}}}"""


async def _helpboard_draft_gemini(prompt: str) -> Optional[dict]:
    """Try Gemini for help post drafting."""
    client = _get_gemini_client()
    if not client:
        return None
    try:
        response = client.models.generate_content(
            model=_get_settings().gemini_model,
            contents=prompt,
        )
        data = _parse_json_from_text(response.text)
        if data and "title" in data and "body" in data:
            return data
        logger.warning("Gemini helpboard_draft: invalid JSON response")
    except Exception as e:
        logger.warning("Gemini helpboard_draft failed: %s", e)
    return None


async def _helpboard_draft_ollama(prompt: str) -> Optional[dict]:
    """Try Ollama for help post drafting."""
    text = await _ollama_generate(prompt, json_mode=True)
    if text:
        data = _parse_json_from_text(text)
        if data and "title" in data and "body" in data:
            return data
        logger.warning("Ollama helpboard_draft: invalid JSON response")
    return None


async def _helpboard_draft_pollinations(prompt: str) -> Optional[dict]:
    """Try Pollinations for help post drafting."""
    text = await _pollinations_generate(prompt, json_mode=True)
    if text:
        data = _parse_json_from_text(text)
        if data and "title" in data and "body" in data:
            return data
        logger.warning("Pollinations helpboard_draft: invalid JSON response")
    return None


async def helpboard_draft(
    description: str,
    help_type: str = "need",
    language: str = "en",
    similar_items: list = None,
) -> tuple[Optional[dict], str]:
    """Draft a help board post using the AI provider cascade.

    Returns (draft_data, provider_name) or (None, "none").
    """
    prompt = _build_helpboard_prompt(description, help_type, language, similar_items)

    providers = _get_provider_order()
    dispatch = {
        "gemini": _helpboard_draft_gemini,
        "ollama": _helpboard_draft_ollama,
        "pollinations": _helpboard_draft_pollinations,
    }

    for provider in providers:
        fn = dispatch.get(provider)
        if fn:
            result = await fn(prompt)
            if result:
                # Validate category
                if result.get("category") not in CATEGORIES:
                    result["category"] = "hand_tools"
                logger.info("helpboard_draft served by %s", provider)
                return result, provider

    return None, "none"



