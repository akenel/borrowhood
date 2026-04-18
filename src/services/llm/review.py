"""Review analysis (sentiment, topics, recommendation score).

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



