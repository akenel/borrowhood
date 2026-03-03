"""Generate unique avatar images for all BorrowHood members.

Uses Pollinations AI (image.pollinations.ai) with varied art styles.
Stores images in MinIO. Updates avatar_url in Postgres.

Run inside Docker network:
  docker exec borrowhood python scripts/generate_avatars.py

Or locally with env vars:
  BH_DATABASE_URL=... BH_MINIO_URL=minio:9000 python scripts/generate_avatars.py
"""

import asyncio
import hashlib
import io
import json
import logging
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

# Pollinations config
POLLINATIONS_URL = "https://image.pollinations.ai"
IMAGE_WIDTH = 512
IMAGE_HEIGHT = 512
DELAY_BETWEEN_REQUESTS = 4  # seconds -- be nice to Pollinations

# MinIO config (from env or defaults for Docker network)
MINIO_URL = os.environ.get("BH_MINIO_URL", "minio:9000")
MINIO_ACCESS_KEY = os.environ.get("BH_MINIO_ACCESS_KEY", "helix_user")
MINIO_SECRET_KEY = os.environ.get("BH_MINIO_SECRET_KEY", "helix_pass")
MINIO_BUCKET = os.environ.get("BH_MINIO_BUCKET", "borrowhood")
MINIO_SECURE = os.environ.get("BH_MINIO_SECURE", "false").lower() == "true"

# DB config
DATABASE_URL = os.environ.get(
    "BH_DATABASE_URL",
    "postgresql+asyncpg://helix_user:helix_pass@postgres:5432/borrowhood"
)

# Art style assignments based on era/personality
STYLE_MAP = {
    # Ancient world -- mosaic, fresco, classical sculpture
    "ancient": "ancient Greek mosaic portrait style, tessellated tiles, warm earth tones, classical face",
    # Medieval -- illuminated manuscript
    "medieval": "medieval illuminated manuscript portrait, gold leaf details, ornate border, tempera paint",
    # Renaissance -- oil painting, chiaroscuro
    "renaissance": "Renaissance oil painting portrait, sfumato technique, warm lighting, detailed features",
    # Baroque -- dramatic, Rembrandt lighting
    "baroque": "Baroque dramatic portrait, Rembrandt lighting, deep shadows, rich colors, oil paint",
    # Classical music -- romantic, soft
    "classical_music": "Romantic era portrait painting, soft focus, warm tones, dignified pose, oil on canvas",
    # Impressionist -- Monet style, soft brush
    "impressionist": "Impressionist portrait, visible brushstrokes, natural light, plein air style, soft focus",
    # Literary -- bookish, thoughtful
    "literary": "Victorian literary portrait, thoughtful expression, warm library lighting, sepia tones",
    # Rock and roll -- gritty, high contrast
    "rock": "gritty rock and roll portrait, high contrast black and white, dramatic shadows, analog film grain",
    # Jazz/blues -- smoky, atmospheric
    "jazz": "smoky jazz club portrait, blue and amber lighting, atmospheric, film noir style",
    # Modern art -- bold, Warhol-esque
    "modern_art": "bold pop art portrait, vibrant colors, screen print style, graphic composition",
    # Computing -- retro terminal, green phosphor
    "computing": "retro computing portrait, green phosphor terminal glow, pixel aesthetic, 1980s tech",
    # Street art -- Banksy style stencil
    "street_art": "street art stencil portrait, spray paint texture, concrete wall background, urban gritty",
    # Contemporary -- clean, magazine quality
    "contemporary": "contemporary magazine portrait, clean lighting, sharp detail, editorial photography style",
    # Activist/truth -- raw documentary
    "activist": "raw documentary portrait, natural light, unflinching gaze, photojournalism style",
    # Community -- warm, friendly, neighborhood
    "community": "warm neighborhood portrait, friendly expression, natural daylight, community feel, watercolor style",
    # Swiss-Canadian/working class -- honest, rugged
    "working_class": "honest working class portrait, weathered hands visible, workshop background, warm natural light",
    # Nomad -- dusty road, freedom
    "nomad": "nomadic traveler portrait, dusty golden hour light, open road background, weathered face",
    # Soul/gospel -- church light, divine
    "soul": "gospel church portrait, stained glass light, warm golden glow, soulful expression",
}

# Map each user slug to an art style
def get_style_for_user(user: dict) -> str:
    """Pick art style based on user's era, skills, or category."""
    slug = user.get("slug", "")
    bio = user.get("bio", "").lower()
    skills = [s.get("category", "") for s in user.get("skills", [])]
    badge = user.get("badge_tier", "newcomer")

    # Specific matches first
    if "banksy" in slug:
        return STYLE_MAP["street_art"]
    if "crowhouse" in slug or "max-igan" in slug:
        return STYLE_MAP["nomad"]
    if any(k in slug for k in ["kenel", "daves-fix", "marios-exc", "pauls-golf"]):
        return STYLE_MAP["working_class"]
    if "angel-hq" in slug:
        return STYLE_MAP["working_class"]

    # Computing legends
    if any(k in slug for k in ["grace", "turing", "ada", "babbage", "shannon", "ritchie",
                                 "thompson", "linus", "berners", "cerf", "neumann", "pascal",
                                 "leonardo", "khwarizmi"]):
        return STYLE_MAP["computing"]

    # Rock legends
    if any(k in slug for k in ["rosetta", "johnson", "chuck", "little-richard", "fats-domino",
                                 "muddy", "elvis", "buddy", "jerry", "bo-diddley", "hendrix"]):
        return STYLE_MAP["rock"]

    # Jazz/blues/soul
    if any(k in slug for k in ["armstrong", "ellington", "billie", "miles", "nina-simone",
                                 "ella-fitz", "aretha", "ray"]):
        return STYLE_MAP["jazz"]
    if "marley" in slug:
        return STYLE_MAP["soul"]

    # Ancient
    if any(k in slug for k in ["homer", "sappho", "euclid", "archimedes", "hypatia"]):
        return STYLE_MAP["ancient"]

    # Medieval/Renaissance
    if any(k in slug for k in ["rumi", "dante"]):
        return STYLE_MAP["medieval"]
    if any(k in slug for k in ["michelangelo", "shakespeare", "leonardo"]):
        return STYLE_MAP["renaissance"]

    # Baroque
    if any(k in slug for k in ["caravaggio", "rembrandt", "bach"]):
        return STYLE_MAP["baroque"]

    # Classical music
    if any(k in slug for k in ["mozart", "beethoven", "chopin", "tchaikovsky", "stravinsky"]):
        return STYLE_MAP["classical_music"]

    # Impressionist
    if any(k in slug for k in ["monet", "van-gogh", "klimt"]):
        return STYLE_MAP["impressionist"]

    # Literary
    if any(k in slug for k in ["twain", "dickens", "tolstoy", "dumas", "emily-dickinson",
                                 "toni-morrison", "garcia-marquez", "borges"]):
        return STYLE_MAP["literary"]

    # Modern art
    if any(k in slug for k in ["picasso", "frida", "okeeffe"]):
        return STYLE_MAP["modern_art"]

    # Contemporary
    if any(k in slug for k in ["dylan", "bowie", "leonard", "joni", "chaplin"]):
        return STYLE_MAP["contemporary"]

    # Activist
    if any(k in slug for k in ["baldwin", "maya-angelou", "fela"]):
        return STYLE_MAP["activist"]

    # Community members (original 34)
    if badge != "legend":
        return STYLE_MAP["community"]

    # Default
    return STYLE_MAP["contemporary"]


def build_avatar_prompt(user: dict) -> str:
    """Build a unique Pollinations prompt for a user's avatar."""
    name = user.get("display_name", "Unknown")
    workshop = user.get("workshop_name", "")
    bio = user.get("bio", "")[:150]
    style = get_style_for_user(user)

    # For Banksy -- no face
    if "banksy" in user.get("slug", ""):
        return f"mysterious hooded figure in shadow, face hidden, holding spray paint can, {style}, portrait format, no text"

    # For anonymous/unknown identity
    if "unknown" in name.lower():
        return f"enigmatic silhouette portrait, {style}, portrait format, no text"

    # Build the prompt
    prompt = f"portrait of {name}, {style}, portrait format, centered face, no text, no watermark"
    return prompt


async def download_image(client: httpx.AsyncClient, prompt: str) -> bytes | None:
    """Download image from Pollinations. Returns bytes or None."""
    encoded = quote(prompt)
    url = f"{POLLINATIONS_URL}/{encoded}?width={IMAGE_WIDTH}&height={IMAGE_HEIGHT}&model=flux&nologo=true&seed={hash(prompt) % 999999}"
    try:
        resp = await client.get(url, follow_redirects=True, timeout=60.0)
        if resp.status_code == 200 and len(resp.content) > 1000:
            return resp.content
        logger.warning(f"Pollinations returned {resp.status_code}, {len(resp.content)} bytes")
    except Exception as e:
        logger.warning(f"Pollinations download failed: {e}")
    return None


def upload_to_minio(slug: str, image_data: bytes) -> str | None:
    """Upload image to MinIO bucket. Returns the object path or None."""
    try:
        from minio import Minio
        client = Minio(
            MINIO_URL,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE,
        )
        # Ensure bucket exists
        if not client.bucket_exists(MINIO_BUCKET):
            client.make_bucket(MINIO_BUCKET)
            logger.info(f"Created MinIO bucket: {MINIO_BUCKET}")

        object_name = f"avatars/{slug}.png"
        client.put_object(
            MINIO_BUCKET,
            object_name,
            io.BytesIO(image_data),
            length=len(image_data),
            content_type="image/png",
        )
        return object_name
    except ImportError:
        logger.error("minio package not installed -- pip install minio")
        return None
    except Exception as e:
        logger.error(f"MinIO upload failed for {slug}: {e}")
        return None


async def update_avatar_url(slug: str, avatar_url: str):
    """Update avatar_url in the database for a user."""
    # Use raw asyncpg for simplicity (no SQLAlchemy needed)
    try:
        import asyncpg
        # Parse DATABASE_URL for asyncpg (strip the +asyncpg part)
        dsn = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        conn = await asyncpg.connect(dsn)
        await conn.execute(
            "UPDATE bh_user SET avatar_url = $1 WHERE slug = $2",
            avatar_url, slug,
        )
        await conn.close()
    except Exception as e:
        logger.error(f"DB update failed for {slug}: {e}")


async def generate_all_avatars():
    """Main function: generate avatars for all BH members."""
    # Load seed data to get user info for prompt building
    seed_path = Path(__file__).parent.parent / "seed_data" / "seed.json"
    with open(seed_path) as f:
        data = json.load(f)

    users = data.get("users", [])
    logger.info(f"Loaded {len(users)} users from seed.json")

    # Check which users already have avatars in MinIO
    existing_avatars = set()
    try:
        from minio import Minio
        client = Minio(
            MINIO_URL,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE,
        )
        if client.bucket_exists(MINIO_BUCKET):
            for obj in client.list_objects(MINIO_BUCKET, prefix="avatars/", recursive=True):
                # Extract slug from avatars/{slug}.png
                name = obj.object_name.replace("avatars/", "").replace(".png", "")
                existing_avatars.add(name)
            logger.info(f"Found {len(existing_avatars)} existing avatars in MinIO")
    except Exception as e:
        logger.warning(f"Could not check MinIO: {e}")

    # Filter to users that need avatars
    todo = [u for u in users if u["slug"] not in existing_avatars]
    logger.info(f"Need to generate {len(todo)} avatars ({len(existing_avatars)} already exist)")

    if not todo:
        logger.info("All avatars already exist. Nothing to do.")
        return

    generated = 0
    failed = 0

    async with httpx.AsyncClient() as client:
        for i, user in enumerate(todo):
            slug = user["slug"]
            prompt = build_avatar_prompt(user)
            logger.info(f"[{i+1}/{len(todo)}] {slug} -- generating...")

            image_data = await download_image(client, prompt)
            if image_data:
                object_name = upload_to_minio(slug, image_data)
                if object_name:
                    # Store as MinIO path -- app will serve via /media/ proxy or direct URL
                    avatar_url = f"/media/{MINIO_BUCKET}/{object_name}"
                    await update_avatar_url(slug, avatar_url)
                    generated += 1
                    logger.info(f"  OK: {slug} ({len(image_data)} bytes) -> {avatar_url}")
                else:
                    failed += 1
                    logger.warning(f"  FAIL (MinIO): {slug}")
            else:
                failed += 1
                logger.warning(f"  FAIL (Pollinations): {slug}")

            # Be nice -- don't flood
            if i < len(todo) - 1:
                logger.info(f"  Waiting {DELAY_BETWEEN_REQUESTS}s...")
                await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

    logger.info(f"DONE: {generated} generated, {failed} failed, {len(existing_avatars)} already existed")


if __name__ == "__main__":
    asyncio.run(generate_all_avatars())
