"""AI service for BorrowHood.

Uses Pollinations.ai free APIs (no key required):
- Text API: listing description generation
- Image API: product image generation for listings

Falls back to Ollama for text if OLLAMA_URL is configured.
Falls back to template-based generation if both are unavailable.
"""

import json
import logging
import os
from typing import Optional
from urllib.parse import quote

import httpx

logger = logging.getLogger(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
POLLINATIONS_TEXT_URL = "https://text.pollinations.ai/"


async def generate_listing_description(
    name: str,
    category: str,
    item_type: str = "physical",
    language: str = "en",
) -> dict:
    """Generate a listing description using AI.

    Returns dict with: title, description, tags (list of 3 strings).
    Tries Pollinations first, then Ollama, then template fallback.
    """
    prompt = _build_listing_prompt(name, category, item_type, language)

    # Try Pollinations first (free, always available)
    result = await _try_pollinations(prompt)
    if result:
        return result

    # Try Ollama if configured
    if OLLAMA_URL:
        result = await _try_ollama(prompt)
        if result:
            return result

    # Template fallback
    return _template_fallback(name, category, item_type, language)


async def generate_skill_bio(
    skill_input: str,
    language: str = "en",
) -> str:
    """Expand a short skill description into a professional bio paragraph."""
    if language == "it":
        prompt = (
            f"Sei un esperto di profili professionali. L'utente ha scritto: \"{skill_input}\". "
            f"Scrivi un paragrafo di 2-3 frasi che descriva questa competenza in modo professionale e amichevole. "
            f"Non usare emoji. Rispondi solo con il testo del bio, nient'altro."
        )
    else:
        prompt = (
            f"You are a professional profile writer. The user typed: \"{skill_input}\". "
            f"Write a 2-3 sentence paragraph that describes this skill professionally and warmly. "
            f"No emoji. Reply with just the bio text, nothing else."
        )

    # Try Pollinations
    result = await _try_pollinations_raw(prompt)
    if result:
        return result.strip()

    # Try Ollama
    if OLLAMA_URL:
        result = await _try_ollama_raw(prompt)
        if result:
            return result.strip()

    # Fallback
    if language == "it":
        return f"Competente in {skill_input}. Esperienza pratica e passione per il mestiere."
    return f"Experienced in {skill_input}. Hands-on skills with a passion for the craft."


def _build_listing_prompt(name: str, category: str, item_type: str, language: str) -> str:
    """Build the prompt for listing generation."""
    if language == "it":
        return (
            f"Sei un esperto di marketplace. Genera una descrizione per un annuncio.\n"
            f"Nome articolo: {name}\n"
            f"Categoria: {category}\n"
            f"Tipo: {item_type}\n\n"
            f"Rispondi SOLO con questo JSON valido, nient'altro:\n"
            f'{{"title": "titolo migliorato", "description": "descrizione di 2-3 frasi", "tags": ["tag1", "tag2", "tag3"]}}'
        )
    return (
        f"You are a marketplace listing expert. Generate a listing description.\n"
        f"Item name: {name}\n"
        f"Category: {category}\n"
        f"Type: {item_type}\n\n"
        f"Reply ONLY with this valid JSON, nothing else:\n"
        f'{{"title": "improved title", "description": "2-3 sentence description", "tags": ["tag1", "tag2", "tag3"]}}'
    )


async def _try_pollinations(prompt: str) -> Optional[dict]:
    """Call Pollinations.ai text API and parse JSON response."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                POLLINATIONS_TEXT_URL,
                json={
                    "messages": [
                        {"role": "system", "content": "You are a helpful marketplace assistant. Reply only with valid JSON."},
                        {"role": "user", "content": prompt},
                    ],
                    "model": "openai",
                    "jsonMode": True,
                },
            )
            if resp.status_code == 200:
                text = resp.text.strip()
                return _parse_json_response(text)
    except Exception as e:
        logger.warning(f"Pollinations API failed: {e}")
    return None


async def _try_pollinations_raw(prompt: str) -> Optional[str]:
    """Call Pollinations for raw text response."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                POLLINATIONS_TEXT_URL,
                json={
                    "messages": [
                        {"role": "user", "content": prompt},
                    ],
                    "model": "openai",
                },
            )
            if resp.status_code == 200:
                return resp.text.strip()
    except Exception as e:
        logger.warning(f"Pollinations raw API failed: {e}")
    return None


async def _try_ollama(prompt: str) -> Optional[dict]:
    """Call Ollama /api/generate and parse JSON response."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                text = data.get("response", "")
                return _parse_json_response(text)
    except Exception as e:
        logger.warning(f"Ollama API failed: {e}")
    return None


async def _try_ollama_raw(prompt: str) -> Optional[str]:
    """Call Ollama for raw text response."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("response", "")
    except Exception as e:
        logger.warning(f"Ollama raw API failed: {e}")
    return None


def _parse_json_response(text: str) -> Optional[dict]:
    """Extract and validate JSON from AI response text."""
    # Strip markdown code fences if present
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

    # Try to find JSON object in the response
    start = text.find("{")
    end = text.rfind("}") + 1
    if start >= 0 and end > start:
        try:
            data = json.loads(text[start:end])
            # Validate required fields
            if "title" in data and "description" in data:
                return {
                    "title": str(data["title"]),
                    "description": str(data["description"]),
                    "tags": [str(t) for t in data.get("tags", [])][:3],
                }
        except json.JSONDecodeError:
            pass
    return None


def _template_fallback(name: str, category: str, item_type: str, language: str) -> dict:
    """Generate a reasonable description from templates when AI is unavailable."""
    templates_en = {
        "tools": f"Well-maintained {name} available in your neighborhood. Perfect for home projects and DIY enthusiasts. Pick up, use it, return it -- no need to buy your own.",
        "kitchen": f"{name} ready to borrow. Great for anyone who loves cooking or baking but doesn't want to buy specialty equipment. Clean and well-cared-for.",
        "garden": f"{name} available for your next garden project. Saves you the cost of buying equipment you'll only use a few times a year.",
        "electronics": f"{name} available to borrow. Fully functional and well-maintained. Save money and reduce e-waste by sharing instead of buying.",
        "sports": f"{name} ready for your next adventure. Try before you buy, or just borrow for the weekend. Equipment sharing at its best.",
        "music": f"{name} available in your community. Perfect for practice sessions, jam sessions, or trying a new instrument without the commitment.",
        "crafts": f"{name} ready for creative projects. Borrow it, make something beautiful, return it. Crafting without the clutter.",
        "cleaning": f"{name} available when you need it. Deep clean your space without buying expensive equipment that sits in storage.",
        "vehicles": f"{name} available for short-term use. Perfect for moving day, weekend trips, or hauling projects.",
    }
    templates_it = {
        "tools": f"{name} ben tenuto, disponibile nel tuo quartiere. Perfetto per progetti fai-da-te. Prendi, usa, restituisci.",
        "kitchen": f"{name} pronto da prendere in prestito. Ideale per chi ama cucinare senza comprare attrezzature specializzate.",
        "garden": f"{name} disponibile per il tuo prossimo progetto in giardino. Risparmia sull'acquisto di attrezzi che usi poche volte l'anno.",
        "electronics": f"{name} disponibile. Funzionante e ben tenuto. Condividi invece di comprare.",
        "sports": f"{name} pronto per la tua prossima avventura. Prova prima di comprare.",
        "music": f"{name} disponibile nella tua comunità. Perfetto per sessioni di pratica.",
        "crafts": f"{name} pronto per progetti creativi. Crea senza ingombrare casa.",
        "cleaning": f"{name} disponibile quando ne hai bisogno. Pulisci a fondo senza comprare attrezzature costose.",
        "vehicles": f"{name} disponibile per uso temporaneo. Perfetto per traslochi o progetti.",
    }

    templates = templates_it if language == "it" else templates_en
    description = templates.get(category, templates_en.get("tools", f"{name} available to borrow in your neighborhood."))

    # Generate tags from category and type
    tag_map = {
        "tools": ["DIY", "home-improvement", "workshop"],
        "kitchen": ["cooking", "baking", "kitchen-gear"],
        "garden": ["gardening", "outdoor", "landscaping"],
        "electronics": ["tech", "gadgets", "electronics"],
        "sports": ["fitness", "outdoor", "adventure"],
        "music": ["instruments", "music", "practice"],
        "crafts": ["creative", "handmade", "art"],
        "cleaning": ["home-care", "deep-clean", "maintenance"],
        "vehicles": ["transport", "moving", "hauling"],
    }

    return {
        "title": name,
        "description": description,
        "tags": tag_map.get(category, ["community", "sharing", "local"]),
    }


def generate_image_url(name: str, category: str) -> str:
    """Generate a product image URL for a listing.

    Uses picsum.photos with a deterministic seed based on item name,
    so the same item always gets the same photo. Free, reliable, no API key.
    """
    # Use item name as seed for consistent, reproducible images
    seed = quote(f"{name}-{category}")
    return f"https://picsum.photos/seed/{seed}/800/600"


async def ensure_item_has_image(db, item_id, name: str, category: str):
    """Auto-generate a Pollinations image if item has no media.

    Called after item creation so items NEVER appear without a picture.
    """
    from sqlalchemy import select, func
    from src.models.item import BHItemMedia, MediaType

    count = await db.scalar(
        select(func.count(BHItemMedia.id)).where(BHItemMedia.item_id == item_id)
    )
    if count and count > 0:
        return  # Item already has at least one image

    image_url = generate_image_url(name, category)
    media = BHItemMedia(
        item_id=item_id,
        url=image_url,
        alt_text=f"{name} - AI generated preview",
        media_type=MediaType.PHOTO,
        sort_order=0,
    )
    db.add(media)
    await db.flush()
    logger.info(f"Auto-generated AI image for item {item_id}")
