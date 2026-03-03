"""Generate unique avatar images for all BorrowHood members.

Uses DiceBear API (api.dicebear.com) with 10 distinct styles mapped to
user eras and personalities. Free, no auth, deterministic (seed-based).

Stores images in MinIO. Updates avatar_url in Postgres.

Run inside Docker network:
  docker exec borrowhood python scripts/generate_avatars.py

Or locally with env vars:
  BH_DATABASE_URL=... BH_MINIO_URL=minio:9000 python scripts/generate_avatars.py
"""

import asyncio
import io
import json
import logging
import os
from pathlib import Path

import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

# DiceBear config
DICEBEAR_URL = "https://api.dicebear.com/9.x"
IMAGE_SIZE = 256  # DiceBear max PNG size
DELAY_BETWEEN_REQUESTS = 1  # seconds -- polite but DiceBear is fast

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

# DiceBear style mapping -- each era/category gets a distinct visual style
# Style reference: https://www.dicebear.com/styles/
STYLE_MAP = {
    # Ancient world -- personas (classic human faces)
    "ancient": "personas",
    # Medieval -- lorelei (elegant, artistic)
    "medieval": "lorelei",
    # Renaissance -- lorelei (refined, dignified)
    "renaissance": "lorelei",
    # Baroque -- personas (dramatic faces)
    "baroque": "personas",
    # Classical music -- notionists (clean, sophisticated)
    "classical_music": "notionists",
    # Impressionist -- open-peeps (sketchy, artistic)
    "impressionist": "open-peeps",
    # Literary -- big-ears (expressive, thoughtful)
    "literary": "big-ears",
    # Rock and roll -- avataaars (bold, iconic)
    "rock": "avataaars",
    # Jazz/blues -- micah (colorful, vibrant)
    "jazz": "micah",
    # Modern art -- micah (bold colors, graphic)
    "modern_art": "micah",
    # Computing -- pixel-art (retro tech)
    "computing": "pixel-art",
    # Street art -- bottts (robotic, urban)
    "street_art": "bottts",
    # Contemporary -- notionists (modern, clean)
    "contemporary": "notionists",
    # Activist -- adventurer (warm, human)
    "activist": "adventurer",
    # Community -- adventurer (friendly, approachable)
    "community": "adventurer",
    # Working class -- big-ears (honest, expressive)
    "working_class": "big-ears",
    # Nomad -- open-peeps (free, sketchy)
    "nomad": "open-peeps",
    # Soul/gospel -- micah (soulful, warm colors)
    "soul": "micah",
}


def get_style_category(user: dict) -> str:
    """Pick style category based on user's era, skills, or personality."""
    slug = user.get("slug", "")
    badge = user.get("badge_tier", "newcomer")

    # Specific matches first
    if "banksy" in slug:
        return "street_art"
    if "crowhouse" in slug or "max-igan" in slug:
        return "nomad"
    if any(k in slug for k in ["kenel", "daves-fix", "marios-exc", "pauls-golf"]):
        return "working_class"
    if "angel-hq" in slug:
        return "working_class"

    # Computing legends
    if any(k in slug for k in ["grace", "turing", "ada", "babbage", "shannon", "ritchie",
                                 "thompson", "linus", "berners", "cerf", "neumann", "pascal",
                                 "leonardo", "khwarizmi"]):
        return "computing"

    # Rock legends
    if any(k in slug for k in ["rosetta", "johnson", "chuck", "little-richard", "fats-domino",
                                 "muddy", "elvis", "buddy", "jerry", "bo-diddley", "hendrix"]):
        return "rock"

    # Jazz/blues/soul
    if any(k in slug for k in ["armstrong", "ellington", "billie", "miles", "nina-simone",
                                 "ella-fitz", "aretha", "ray"]):
        return "jazz"
    if "marley" in slug:
        return "soul"

    # Ancient
    if any(k in slug for k in ["homer", "sappho", "euclid", "archimedes", "hypatia"]):
        return "ancient"

    # Medieval/Renaissance
    if any(k in slug for k in ["rumi", "dante"]):
        return "medieval"
    if any(k in slug for k in ["michelangelo", "shakespeare", "leonardo"]):
        return "renaissance"

    # Baroque
    if any(k in slug for k in ["caravaggio", "rembrandt", "bach"]):
        return "baroque"

    # Classical music
    if any(k in slug for k in ["mozart", "beethoven", "chopin", "tchaikovsky", "stravinsky"]):
        return "classical_music"

    # Impressionist
    if any(k in slug for k in ["monet", "van-gogh", "klimt"]):
        return "impressionist"

    # Literary
    if any(k in slug for k in ["twain", "dickens", "tolstoy", "dumas", "emily-dickinson",
                                 "toni-morrison", "garcia-marquez", "borges"]):
        return "literary"

    # Modern art
    if any(k in slug for k in ["picasso", "frida", "okeeffe"]):
        return "modern_art"

    # Contemporary
    if any(k in slug for k in ["dylan", "bowie", "leonard", "joni", "chaplin", "tesla"]):
        return "contemporary"

    # Activist
    if any(k in slug for k in ["baldwin", "maya-angelou", "fela"]):
        return "activist"

    # Community members (original 34)
    if badge != "legend":
        return "community"

    # Default for uncategorized legends
    return "contemporary"


def get_dicebear_url(slug: str, style: str) -> str:
    """Build DiceBear API URL for a user's avatar."""
    return f"{DICEBEAR_URL}/{style}/png?seed={slug}&size={IMAGE_SIZE}&radius=50"


async def download_avatar(client: httpx.AsyncClient, slug: str, style: str) -> bytes | None:
    """Download avatar from DiceBear. Returns bytes or None."""
    url = get_dicebear_url(slug, style)
    try:
        resp = await client.get(url, follow_redirects=True, timeout=30.0)
        if resp.status_code == 200 and len(resp.content) > 500:
            return resp.content
        logger.warning(f"DiceBear returned {resp.status_code}, {len(resp.content)} bytes for {slug}")
    except Exception as e:
        logger.warning(f"DiceBear download failed for {slug}: {e}")
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
    try:
        import asyncpg
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

    # Show style distribution
    style_counts = {}
    for u in todo:
        cat = get_style_category(u)
        style = STYLE_MAP[cat]
        style_counts[style] = style_counts.get(style, 0) + 1
    logger.info(f"Style distribution: {dict(sorted(style_counts.items()))}")

    generated = 0
    failed = 0

    async with httpx.AsyncClient() as client:
        for i, user in enumerate(todo):
            slug = user["slug"]
            category = get_style_category(user)
            style = STYLE_MAP[category]
            logger.info(f"[{i+1}/{len(todo)}] {slug} ({category} -> {style})")

            image_data = await download_avatar(client, slug, style)
            if image_data:
                object_name = upload_to_minio(slug, image_data)
                if object_name:
                    avatar_url = f"/media/{MINIO_BUCKET}/{object_name}"
                    await update_avatar_url(slug, avatar_url)
                    generated += 1
                    logger.info(f"  OK: {len(image_data)} bytes -> {avatar_url}")
                else:
                    failed += 1
                    logger.warning(f"  FAIL (MinIO): {slug}")
            else:
                failed += 1
                logger.warning(f"  FAIL (DiceBear): {slug}")

            # Polite delay
            if i < len(todo) - 1:
                await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

    logger.info(f"DONE: {generated} generated, {failed} failed, {len(existing_avatars)} already existed")


if __name__ == "__main__":
    asyncio.run(generate_all_avatars())
