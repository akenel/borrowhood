"""Suggest skills from a user bio using AI.

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
    CATEGORIES,
)

logger = logging.getLogger(__name__)

# ── Skill Suggestions from Bio ──────────────────────────────────────


def _build_skills_prompt(bio: str, existing_skills: list = None) -> str:
    """Build prompt for extracting skills from a user bio."""
    existing_text = ""
    if existing_skills:
        existing_text = "\n\nUSER ALREADY HAS THESE SKILLS (do not suggest duplicates):\n"
        for s in existing_skills:
            existing_text += f"- {s}\n"

    categories_str = ", ".join(CATEGORIES)

    return f"""You are a skill extraction assistant for La Piazza, a neighborhood sharing platform.

Analyze this user's bio and extract concrete, marketable skills.

BIO:
\"\"\"{bio}\"\"\"
{existing_text}

RULES:
- Extract only CONCRETE skills (e.g., "TIG Welding", "Bread Baking", "Python Programming")
- Do NOT extract soft skills (e.g., "hard worker", "team player", "passionate")
- Estimate years of experience from context clues in the bio
- Suggest a self_rating from 1-5 based on how the person describes their expertise
- Pick a category for each skill from: {categories_str}
- Return maximum 8 suggestions
- If the bio mentions certifications or professional experience, rate higher (4-5)
- If the bio mentions hobby or learning, rate lower (2-3)

Reply ONLY with this JSON:
{{
  "skills": [
    {{
      "skill_name": "Skill Name",
      "category": "valid_category",
      "self_rating": 3,
      "years_experience": 5,
      "confidence": 0.85
    }}
  ]
}}"""


async def _skills_gemini(prompt: str) -> Optional[dict]:
    """Try Gemini for skill extraction."""
    client = _get_gemini_client()
    if not client:
        return None
    try:
        response = client.models.generate_content(
            model=_get_settings().gemini_model,
            contents=prompt,
        )
        data = _parse_json_from_text(response.text)
        if data and "skills" in data:
            return data
        logger.warning("Gemini suggest_skills: invalid JSON response")
    except Exception as e:
        logger.warning("Gemini suggest_skills failed: %s", e)
    return None


async def _skills_ollama(prompt: str) -> Optional[dict]:
    """Try Ollama for skill extraction."""
    text = await _ollama_generate(prompt, json_mode=True)
    if text:
        data = _parse_json_from_text(text)
        if data and "skills" in data:
            return data
        logger.warning("Ollama suggest_skills: invalid JSON response")
    return None


async def _skills_pollinations(prompt: str) -> Optional[dict]:
    """Try Pollinations for skill extraction."""
    text = await _pollinations_generate(prompt, json_mode=True)
    if text:
        data = _parse_json_from_text(text)
        if data and "skills" in data:
            return data
        logger.warning("Pollinations suggest_skills: invalid JSON response")
    return None


async def suggest_skills_from_bio(
    bio: str,
    existing_skills: list = None,
) -> tuple[Optional[list], str]:
    """Extract skills from user bio using the AI provider cascade.

    Returns (skills_list, provider_name) or (None, "none").
    """
    prompt = _build_skills_prompt(bio, existing_skills)

    providers = _get_provider_order()
    dispatch = {
        "gemini": _skills_gemini,
        "ollama": _skills_ollama,
        "pollinations": _skills_pollinations,
    }

    for provider in providers:
        fn = dispatch.get(provider)
        if fn:
            result = await fn(prompt)
            if result and result.get("skills"):
                for skill in result["skills"]:
                    if skill.get("category") not in CATEGORIES:
                        skill["category"] = "other"
                    skill["self_rating"] = max(1, min(5, skill.get("self_rating", 3)))
                    skill["confidence"] = max(0.0, min(1.0, skill.get("confidence", 0.5)))
                logger.info("suggest_skills served by %s (%d skills)", provider, len(result["skills"]))
                return result["skills"], provider

    return None, "none"


