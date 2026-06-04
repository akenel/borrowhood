"""Ollama Turbo compression for Locandina + Bio postcard description blocks.

Block 4 of the Locandina roadmap (2026-06-04). Owner-typed descriptions
that exceed the printable card's 250-char slot get compressed into a
200-250 char card-ready hook using Ollama Turbo (Angel's $20/mo flat
sub via BH_OLLAMA_KEY).

See memory: feedback-lean-hard-on-ollama-summarization.

Output bands:
    Locandina description: 200-250 chars (this module's default)
    Bio postcard description: 300-500 chars (caller overrides target_max)

Editable on preview: the result is cached on the parent row
(bh_listing.locandina_summary OR bh_user.bio_card_summary) and the
preview page lets the owner override the AI text with their own words.
"""
from __future__ import annotations

import logging
from typing import Optional

from src.services.llm._common import _ollama_generate

logger = logging.getLogger(__name__)


def _build_prompt(
    description: str,
    story: Optional[str],
    lang: str,
    target_min: int,
    target_max: int,
) -> str:
    """Compose the compression prompt for Ollama. Plain text output, no JSON."""
    lang_name = "Italian" if lang == "it" else "English"
    story_block = f"\n\nAdditional context (the story):\n{story.strip()}" if story and story.strip() else ""
    return (
        f"You are compressing an event/listing description for a printable A6 postcard.\n"
        f"Write the output in {lang_name}.\n"
        f"Target: between {target_min} and {target_max} characters total.\n"
        f"Keep the hook, the value proposition, who it's for, and what they walk away with.\n"
        f"Drop redundancy, hedging, and meta-commentary. Active voice, present tense.\n"
        f"Do NOT include preamble, quotes, brackets, hashtags, or JSON. Reply with only the\n"
        f"compressed description as plain prose.\n\n"
        f"Original description:\n{description.strip()}"
        f"{story_block}"
    )


async def generate_locandina_summary(
    description: str,
    story: Optional[str] = None,
    lang: str = "en",
    target_min: int = 200,
    target_max: int = 250,
) -> Optional[str]:
    """Compress description (+story) into a printable card-ready hook.

    Returns the compressed text on success, or None if Ollama is unreachable
    or the response is empty / clearly malformed (caller should fall back
    to truncation stub).

    Idempotent and stateless -- caller is responsible for caching.
    """
    if not description or not description.strip():
        return None

    prompt = _build_prompt(description, story, lang, target_min, target_max)
    raw = await _ollama_generate(prompt, json_mode=False)
    if not raw:
        logger.warning("locandina_summary: ollama returned empty/none")
        return None

    text = raw.strip().strip('"').strip("'").strip()
    # Strip a leading "Compressed description:" or similar preamble.
    for prefix in ("Compressed description:", "Summary:", "Description:", "Output:"):
        if text.lower().startswith(prefix.lower()):
            text = text[len(prefix):].strip()
            break

    if not text:
        return None

    # If Ollama went long (some models ignore char limits), clamp to target_max
    # at a word boundary so the cached value never overflows the print slot.
    if len(text) > target_max:
        # Find the last space at or before target_max - 3 (room for ellipsis)
        cut = text.rfind(" ", 0, target_max - 3)
        if cut > target_min // 2:
            text = text[:cut].rstrip() + "..."
        else:
            text = text[: target_max - 3].rstrip() + "..."

    return text
