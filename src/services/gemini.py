"""Backward-compat shim — gemini.py was split into src/services/ai/.

This module re-exports the public functions so existing imports keep
working:
    from src.services.gemini import smart_listing, review_analysis,
        concierge_search, helpboard_draft, suggest_skills_from_bio

New code should import from src.services.ai directly.
"""

from src.services.llm import (
    smart_listing,
    review_analysis,
    concierge_search,
    helpboard_draft,
    suggest_skills_from_bio,
)

__all__ = [
    "smart_listing",
    "review_analysis",
    "concierge_search",
    "helpboard_draft",
    "suggest_skills_from_bio",
]
