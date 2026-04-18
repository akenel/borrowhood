"""llm/ — AI service cascade split by domain.

Public entry points mirror the original gemini.py module-level API:
    from src.services.llm import smart_listing, review_analysis,
        concierge_search, helpboard_draft, suggest_skills_from_bio
"""

from .listing import smart_listing
from .review import review_analysis
from .concierge import concierge_search
from .helpboard import helpboard_draft
from .skills import suggest_skills_from_bio

# Shared infra (rarely imported directly but kept public for tests/utility)
from ._common import (
    _get_settings,
    _get_gemini_client,
    _get_provider_order,
    _parse_json_from_text,
    _ollama_generate,
    _pollinations_generate,
)

__all__ = [
    "smart_listing",
    "review_analysis",
    "concierge_search",
    "helpboard_draft",
    "suggest_skills_from_bio",
]
