"""Multi-provider AI service for BorrowHood.

Provider cascade (configurable via BH_AI_PROVIDER):
  auto     -> gemini -> ollama -> pollinations -> template fallback
  gemini   -> gemini only (fails gracefully if unavailable)
  ollama   -> ollama only
  pollinations -> pollinations only

Gemini:       Google API, free tier 20 req/day -- use for competitions/demos
Ollama Turbo: Self-hosted, 20+ models, unlimited, turbo speeds -- daily workhorse
Pollinations: Free cloud API, no key needed -- always-on fallback

"We do Google for money, but we run Pollinations and Ollama Turbo."
"""

import json
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Lazy imports -- google-genai may not be installed in all environments
_genai = None

# Valid categories (must match src/models/item.py)
CATEGORIES = [
    "power_tools", "hand_tools", "automotive", "welding", "woodworking",
    "3d_printing", "kitchen", "cleaning", "garden", "furniture",
    "home_improvement", "sports", "camping", "water_sports", "cycling",
    "art", "music", "photography", "sewing", "electronics", "computers",
    "drones", "spaces", "vehicles", "repairs", "training_service",
    "custom_orders", "fashion", "books", "kids", "pets",
]

# Review weight multipliers by badge tier
REVIEW_WEIGHTS = {
    "NEWCOMER": 1.0, "ACTIVE": 2.0, "TRUSTED": 5.0,
    "PILLAR": 8.0, "LEGEND": 10.0,
}

POLLINATIONS_TEXT_URL = "https://text.pollinations.ai/"


def _get_settings():
    """Lazy import of app settings."""
    from src.config import settings
    return settings


# ── Provider clients ─────────────────────────────────────────────────


def _get_gemini_client():
    """Create Gemini client if API key is configured."""
    global _genai
    s = _get_settings()

    if not s.google_api_key:
        return None

    if _genai is None:
        try:
            from google import genai as genai_module
            _genai = genai_module
        except ImportError:
            logger.warning("google-genai not installed -- Gemini disabled")
            return None

    return _genai.Client(api_key=s.google_api_key)


def _get_provider_order() -> list:
    """Return ordered list of providers to try based on BH_AI_PROVIDER setting."""
    s = _get_settings()
    provider = s.ai_provider.lower().strip()

    if provider == "gemini":
        return ["gemini"]
    elif provider == "ollama":
        return ["ollama"]
    elif provider == "pollinations":
        return ["pollinations"]
    else:  # "auto" or anything else
        return ["gemini", "ollama", "pollinations"]


# ── JSON parsing ─────────────────────────────────────────────────────


def _parse_json_from_text(text: str) -> Optional[dict]:
    """Extract JSON object from AI response text."""
    # Strip markdown code fences
    if "```" in text:
        lines = text.split("\n")
        json_lines = []
        inside = False
        for line in lines:
            if line.strip().startswith("```"):
                inside = not inside
                continue
            if inside:
                json_lines.append(line)
        text = "\n".join(json_lines)

    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            return json.loads(text[start:end])
        except json.JSONDecodeError:
            pass
    return None


# ── Ollama helpers ───────────────────────────────────────────────────


async def _ollama_generate(prompt: str, json_mode: bool = True) -> Optional[str]:
    """Call Ollama /api/generate. Works with local or Turbo cloud.

    Local:  BH_OLLAMA_URL=http://localhost:11434 (no key needed)
    Cloud:  BH_OLLAMA_URL=https://ollama.com + BH_OLLAMA_KEY
    """
    s = _get_settings()
    if not s.ollama_url:
        return None

    payload = {
        "model": s.ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    if json_mode:
        payload["format"] = "json"

    headers = {"Content-Type": "application/json"}
    if s.ollama_key:
        headers["Authorization"] = f"Bearer {s.ollama_key}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{s.ollama_url.rstrip('/')}/api/generate",
                json=payload,
                headers=headers,
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("response", "")
            logger.warning("Ollama API returned %s: %s", resp.status_code, resp.text[:200])
    except Exception as e:
        logger.warning("Ollama API failed: %s", e)
    return None


# ── Pollinations helpers ─────────────────────────────────────────────


async def _pollinations_generate(prompt: str, json_mode: bool = True) -> Optional[str]:
    """Call Pollinations.ai text API. Returns raw text response or None."""
    messages = [{"role": "user", "content": prompt}]
    if json_mode:
        messages.insert(0, {
            "role": "system",
            "content": "You are a helpful assistant. Reply only with valid JSON.",
        })

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                POLLINATIONS_TEXT_URL,
                json={
                    "messages": messages,
                    "model": "openai",
                    "jsonMode": json_mode,
                },
            )
            if resp.status_code == 200:
                return resp.text.strip()
    except Exception as e:
        logger.warning("Pollinations API failed: %s", e)
    return None


# ── Smart Listing ────────────────────────────────────────────────────


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

    return f"""You are the Smart Listing Assistant for BorrowHood, a neighborhood sharing platform
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


# ── Review Analysis ──────────────────────────────────────────────────


def _build_review_prompt(
    user_name: str, badge_tier: str, reviews: list,
    review_count: int, average_rating: float,
) -> str:
    """Build the review analysis prompt used by all providers."""
    reviews_text = ""
    for r in reviews:
        reviews_text += (
            f"- Rating: {r.get('rating', '?')}/5, "
            f"Title: \"{r.get('title', '')}\", "
            f"Body: \"{r.get('body', '')}\", "
            f"Reviewer tier: {r.get('reviewer_tier', 'NEWCOMER')}, "
            f"Weight: {r.get('weight', 1.0)}, "
            f"Skill: {r.get('skill_name', 'n/a')}, "
            f"Skill rating: {r.get('skill_rating', 'n/a')}\n"
        )

    weights_text = ", ".join(f"{k}={v}x" for k, v in REVIEW_WEIGHTS.items())

    return f"""Analyze reviews for {user_name} (badge tier: {badge_tier}).

REVIEW WEIGHT SYSTEM: {weights_text}
A review from a Legend carries 10x the weight of a Newcomer.

REVIEWS ({len(reviews)} total, average rating: {average_rating:.1f}):
{reviews_text}

ANALYZE:
1. Sentiment: count positive (4-5 stars), neutral (3), negative (1-2)
2. Fake review detection: flag suspicious patterns (NEWCOMER clusters, identical text, empty 5-stars)
3. Skill insights: group by skill if present
4. Keywords: most mentioned positive and negative themes
5. Summary: 2-3 sentences about this person's reputation

Reply ONLY with this JSON:
{{
  "user_name": "{user_name}",
  "badge_tier": "{badge_tier}",
  "total_reviews": {len(reviews)},
  "sentiment": {{"positive": 0, "neutral": 0, "negative": 0}},
  "average_rating": {average_rating:.1f},
  "weighted_average": 0.0,
  "fake_review_flags": [],
  "skill_insights": [{{"skill": "...", "avg_rating": 0.0, "review_count": 0, "trend": "stable"}}],
  "top_keywords": {{"positive": [], "negative": []}},
  "summary": "..."
}}"""


async def _review_gemini(prompt: str) -> Optional[dict]:
    """Try Gemini for review analysis."""
    client = _get_gemini_client()
    if not client:
        return None
    try:
        response = client.models.generate_content(
            model=_get_settings().gemini_model,
            contents=prompt,
        )
        data = _parse_json_from_text(response.text)
        if data and "summary" in data:
            return data
        logger.warning("Gemini review_analysis: invalid JSON response")
    except Exception as e:
        logger.warning("Gemini review_analysis failed: %s", e)
    return None


async def _review_ollama(prompt: str) -> Optional[dict]:
    """Try Ollama for review analysis."""
    text = await _ollama_generate(prompt, json_mode=True)
    if text:
        data = _parse_json_from_text(text)
        if data and "summary" in data:
            return data
        logger.warning("Ollama review_analysis: invalid JSON response")
    return None


async def _review_pollinations(prompt: str) -> Optional[dict]:
    """Try Pollinations for review analysis."""
    text = await _pollinations_generate(prompt, json_mode=True)
    if text:
        data = _parse_json_from_text(text)
        if data and "summary" in data:
            return data
        logger.warning("Pollinations review_analysis: invalid JSON response")
    return None


async def review_analysis(
    user_name: str,
    badge_tier: str,
    reviews: list,
    review_count: int = 0,
    average_rating: float = 0.0,
) -> tuple[Optional[dict], str]:
    """Analyze reviews using the AI provider cascade.

    Returns (analysis_data, provider_name) or (None, "none").
    """
    if not reviews:
        return {
            "user_name": user_name,
            "badge_tier": badge_tier,
            "total_reviews": 0,
            "sentiment": {"positive": 0, "neutral": 0, "negative": 0},
            "average_rating": 0.0,
            "weighted_average": 0.0,
            "fake_review_flags": [],
            "skill_insights": [],
            "top_keywords": {"positive": [], "negative": []},
            "summary": f"{user_name} has no reviews yet. Complete some rentals to start building reputation.",
        }, "template"

    prompt = _build_review_prompt(user_name, badge_tier, reviews, review_count, average_rating)

    providers = _get_provider_order()
    dispatch = {
        "gemini": _review_gemini,
        "ollama": _review_ollama,
        "pollinations": _review_pollinations,
    }

    for provider in providers:
        fn = dispatch.get(provider)
        if fn:
            result = await fn(prompt)
            if result:
                logger.info("review_analysis served by %s", provider)
                return result, provider

    return None, "none"


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

    return f"""You are the AI Concierge for BorrowHood, a neighborhood sharing platform
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


# ── Help Board AI Draft ──────────────────────────────────────────────


def _build_helpboard_prompt(description: str, help_type: str, language: str, similar_items: list = None) -> str:
    """Build prompt for AI-assisted help post drafting."""
    items_text = ""
    if similar_items:
        items_text = "\n\nSIMILAR ITEMS ON THE PLATFORM:\n"
        for item in similar_items[:5]:
            items_text += f"- {item['name']} (category: {item.get('category', '?')}, price: EUR {item.get('price', '?')}/day)\n"

    lang_instruction = f"Write the title and body in {language}." if language != "en" else ""

    return f"""You are the AI assistant for BorrowHood, a community sharing platform.

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
