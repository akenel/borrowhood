"""Gemini AI service for BorrowHood.

Uses Google's Gemini API (gemini-2.5-flash) for:
- Smart listing generation (richer than Pollinations)
- Review sentiment analysis with weighted reputation
- Natural language concierge search

Falls back to existing Pollinations/template generators on failure.
"""

import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy import -- google-genai may not be installed in all environments
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


def _get_settings():
    """Lazy import of app settings."""
    from src.config import settings
    return settings


def _get_client():
    """Create Gemini client if API key is configured."""
    global _genai
    s = _get_settings()

    if not s.google_api_key:
        logger.warning("BH_GOOGLE_API_KEY not set -- Gemini features disabled")
        return None

    if _genai is None:
        try:
            from google import genai as genai_module
            _genai = genai_module
        except ImportError:
            logger.warning("google-genai not installed -- Gemini features disabled")
            return None

    return _genai.Client(api_key=s.google_api_key)


def _parse_json_from_text(text: str) -> Optional[dict]:
    """Extract JSON object from Gemini response text."""
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


async def smart_listing(
    name: str,
    category: str = "",
    item_type: str = "physical",
    language: str = "en",
    similar_items: list = None,
) -> Optional[dict]:
    """Generate a complete listing using Gemini.

    Returns rich listing data (title, description, category, price, deposit,
    story, tags) or None if Gemini is unavailable.
    """
    client = _get_client()
    if not client:
        return None

    # Build context about similar items for price calibration
    similar_context = ""
    if similar_items:
        similar_context = "\n\nSIMILAR ITEMS ON THE PLATFORM (for price calibration):\n"
        for item in similar_items[:5]:
            similar_context += f"- {item.get('name', '?')}: {item.get('category', '?')}\n"

    categories_str = ", ".join(CATEGORIES)

    prompt = f"""You are the Smart Listing Assistant for BorrowHood, a neighborhood sharing platform
in Trapani, Sicily. Generate a complete listing from the item info below.

Item name: {name}
Category hint: {category or 'auto-detect'}
Item type: {item_type}
Language: {language}
{similar_context}

VALID CATEGORIES: {categories_str}

RULES:
- The Grandma Test: if an 83-year-old can't understand it, rewrite it.
- Prices should be fair for a neighborhood. EUR 3-15/day for most tools.
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

    try:
        response = client.models.generate_content(
            model=_get_settings().gemini_model,
            contents=prompt,
        )
        data = _parse_json_from_text(response.text)
        if data and "title" in data and "description" in data:
            # Validate category
            if data.get("category") not in CATEGORIES:
                data["category"] = category or "hand_tools"
            return data
        logger.warning("Gemini smart_listing: invalid JSON response")
    except Exception as e:
        logger.warning("Gemini smart_listing failed: %s", e)

    return None


async def review_analysis(
    user_name: str,
    badge_tier: str,
    reviews: list,
    review_count: int = 0,
    average_rating: float = 0.0,
) -> Optional[dict]:
    """Analyze reviews for a user using Gemini.

    Returns sentiment breakdown, fake review flags, keywords, and summary.
    """
    client = _get_client()
    if not client:
        return None

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
        }

    # Format reviews for Gemini
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

    prompt = f"""Analyze reviews for {user_name} (badge tier: {badge_tier}).

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


async def concierge_search(
    query: str,
    language: str = "en",
    items: list = None,
    members: list = None,
) -> Optional[dict]:
    """Natural language search interpretation using Gemini.

    Given search results from the database, Gemini formats a friendly response
    with match reasons and suggestions.
    """
    client = _get_client()
    if not client:
        return None

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

    prompt = f"""You are the AI Concierge for BorrowHood, a neighborhood sharing platform
in Trapani, Sicily. A user searched for: "{query}"

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
