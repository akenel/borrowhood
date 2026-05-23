"""AI provider cascade shared infra.

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


import asyncio
import json
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

# Gemini SDK calls are SYNCHRONOUS. Without the helper below they block the
# event loop AND have no timeout, which lets a slow Gemini hang the whole
# FastAPI worker (BL-2 was exactly this failure mode on /helpboard).
# Task #29 (2026-05-23) lifts the pattern out of helpboard.py so all five
# Gemini-using services (helpboard, skills, listing, review, concierge)
# share the same hang-protection.
GEMINI_TIMEOUT_S = 15.0

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


async def _gemini_call_text(prompt: str, *, timeout: Optional[float] = None) -> Optional[str]:
    """Call Gemini generate_content() with timeout + thread offload.

    Returns response.text on success, or None on:
      - No client configured (no GOOGLE_API_KEY)
      - Timeout (logged at WARNING)
      - Any other SDK exception (logged at WARNING)

    Callers parse the returned text and validate per their schema. The
    cascade in their dispatch dict naturally falls through to the next
    provider (Ollama, then Pollinations) when this returns None.

    Default timeout resolves to GEMINI_TIMEOUT_S at CALL time (not at
    function-definition time) so tests can monkeypatch the module
    constant and have the new value take effect.

    Task #29 helper -- replaces five copies of this pattern across
    helpboard, skills, listing, review, concierge.
    """
    client = _get_gemini_client()
    if not client:
        return None
    effective_timeout = timeout if timeout is not None else GEMINI_TIMEOUT_S
    s = _get_settings()
    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(
                client.models.generate_content,
                model=s.gemini_model,
                contents=prompt,
            ),
            timeout=effective_timeout,
        )
        return response.text
    except asyncio.TimeoutError:
        logger.warning("Gemini call timed out after %ss", effective_timeout)
    except Exception as e:
        logger.warning("Gemini call failed: %s", e)
    return None


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
    else:  # "auto" or anything else -- Ollama Turbo is paid+reliable, Pollinations is images only
        return ["gemini", "ollama"]


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
        async with httpx.AsyncClient(timeout=30.0) as client:
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


