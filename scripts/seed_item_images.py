"""Seed item images from Unsplash for items that have no media.

Uses curated Unsplash photo IDs per category. Each category gets 8-12 photos
that rotate across its items (deterministic by item index).

Unsplash URLs are stable, free, no auth required. Format:
  https://images.unsplash.com/photo-{ID}?w=800&h=600&fit=crop&q=80

Run inside Docker network:
  docker exec borrowhood python scripts/seed_item_images.py

Or locally:
  BH_DATABASE_URL=... python scripts/seed_item_images.py
"""

import asyncio
import logging
import os
import uuid

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get(
    "BH_DATABASE_URL",
    "postgresql+asyncpg://helix_user:helix_pass@postgres:5432/borrowhood"
)

# Curated Unsplash photo IDs per category
# Each photo chosen for visual quality and relevance
CATEGORY_PHOTOS = {
    "art": [
        "1579783928621-7a13d66a62d1",  # paint brushes
        "1513364776144-60967b0f800f",  # colorful art supplies
        "1460661419201-fd4cecdf8a8b",  # watercolor palette
        "1596548438137-d426bddcef5e",  # painting canvas
        "1513475382121-6e4fc66bed2b",  # sculpture studio
        "1541961017774-22349e4a1262",  # art gallery
        "1547891654-e66ed7ebb968",     # sketch pencils
        "1499892477393-f675706cbe6e",  # ceramic pottery
        "1452587925148-ce544e77e70d",  # drawing tools
        "1551732998-9573f8ede610",     # art workshop
    ],
    "sports": [
        "1461896836934-ffe607ba8211",  # weights gym
        "1571019614242-c5c5dee9f50c",  # boxing gloves
        "1534438327276-14e5300c3a48",  # gym equipment
        "1517963879433-6ad2b056d712",  # running shoes
        "1552674605-db6ffd4facb5",     # martial arts
        "1518611012118-696072aa579a",  # sports equipment
        "1574629810360-7efbbe195018",  # training ropes
        "1526506118085-60ce8714f8c5",  # dumbbell
        "1599058917212-d750089bc07e",  # combat training
        "1549060279-7e168fcee0c2",     # sports arena
    ],
    "education": [
        "1503676260728-1c00da094a0b",  # classroom
        "1524178232363-1fb2b075b655",  # lecture hall
        "1427504494785-3a9ca7044f45",  # books stack
        "1509062522246-3755977927d7",  # workshop teaching
        "1488190211105-8b0e65b80b4e",  # tutoring
        "1577896851231-d472b2651ad3",  # training session
        "1523050854058-8df90110c6f1",  # whiteboard
        "1531545514256-b1400bc00f31",  # learning
        "1516321318423-f06f85e504b3",  # group workshop
        "1491975474562-1f4e30bc9468",  # mentoring
    ],
    "science": [
        "1532094349884-543bc11b234d",  # laboratory
        "1507413245164-6160d8298b44",  # microscope
        "1628595351029-c2bf17511435",  # chemistry lab
        "1576086213369-97a306d36557",  # test tubes
        "1518152006812-edab29b069ac",  # scientific equipment
        "1559757175-5700dde675bc",     # telescope
        "1614935151651-0bea6508db6b",  # physics lab
        "1581093450021-4a7360e9a6b5",  # science experiment
        "1635070041078-e363dbe005cb",  # lab equipment
        "1507413245164-6160d8298b44",  # research
    ],
    "music": [
        "1511379938547-c1f69419868d",  # guitar
        "1493225457124-a3eb161ffa5f",  # piano keys
        "1507838153414-b4b713384a76",  # vinyl records
        "1514320291840-2e0a9bf2a9ae",  # microphone
        "1459749411175-04bf5292ceea",  # drums
        "1510915361894-db8b60106cb1",  # concert
        "1558618666-fcd25c85f7e7",     # saxophone
        "1519683384663-d7fd26ec2da9",  # cello
        "1525201548942-d8732f6617a0",  # sheet music
        "1508854710579-5cecc3a9ff17",  # studio recording
    ],
    "tools": [
        "1504148455328-c376907d081c",  # workshop tools
        "1530124566582-a45a7e3e25f7",  # hand tools wall
        "1572981779307-38b8cabb2407",  # workbench
        "1426927308491-6380b6a9936f",  # hammer wrench
        "1518709766631-a6a7f45921c3",  # toolbox
        "1581783898377-1c85bf937427",  # power drill
        "1513467535987-cd81b4d5e4d0",  # workshop
        "1558618666-fcd25c85f7e7",     # repair tools
        "1585771724684-38269d6639fd",  # vintage tools
        "1543520080-a6f04a0cd241",     # carpentry
    ],
    "electronics": [
        "1518770660439-4636190af475",  # circuit board
        "1555664424-51030bb2a12d",     # electronics lab
        "1581092160607-ee22621dd933",  # arduino
        "1517077304055-6e89beddb7b0",  # soldering
        "1588508065123-287b28e013da",  # multimeter
        "1550751827-4bd374c3f58b",     # electronic components
        "1518770660439-4636190af475",  # tech workspace
        "1581092918056-0c4c3acd3789",  # raspberry pi
    ],
    "engineering": [
        "1581091226825-a6a2a5aee158",  # engineering blueprints
        "1504917595217-d4dc5ede4baa",  # 3d printing
        "1537462715879-360eeb61a0ad",  # robotics
        "1565043589221-f4024e9f0c34",  # mechanical parts
        "1518770660439-4636190af475",  # prototyping
        "1635070041078-e363dbe005cb",  # engineering lab
        "1581092160607-ee22621dd933",  # maker space
        "1504917595217-d4dc5ede4baa",  # fabrication
    ],
    "outdoor": [
        "1504280390367-361c6d9f38f4",  # hiking gear
        "1478827536114-da961b7f86d2",  # camping tent
        "1510312305653-8ed496efae75",  # outdoor adventure
        "1496545672447-f699b503d270",  # compass map
        "1551632811-561732d1e306",     # kayak
        "1527004013197-933c4588c6af",  # climbing
        "1504851149312-7a075b496cc7",  # trail
        "1517164850305-20a35bd6734c",  # survival gear
    ],
    "garden": [
        "1416879595882-3373a0480b5b",  # garden tools
        "1585320806297-9794b3e4eeae",  # gardening
        "1523348837708-15d4fc89cba7",  # planting
        "1466692476868-aef1dfb1e735",  # herbs garden
        "1591857177580-dc82b9ac4e1e",  # greenhouse
        "1558171813-4c2ab4e78220",     # watering plants
    ],
    "hand_tools": [
        "1504148455328-c376907d081c",  # hand tools
        "1530124566582-a45a7e3e25f7",  # tool wall
        "1426927308491-6380b6a9936f",  # wrench hammer
    ],
    "crafts": [
        "1452587925148-ce544e77e70d",  # crafting
    ],
    "food": [
        "1556909114-f6e7ad7d3136",     # cooking
    ],
    "other": [
        "1504148455328-c376907d081c",  # general workshop
    ],
}

# Fallback for unmapped categories
DEFAULT_PHOTOS = [
    "1504148455328-c376907d081c",
    "1513467535987-cd81b4d5e4d0",
    "1572981779307-38b8cabb2407",
]


def unsplash_url(photo_id: str) -> str:
    """Build Unsplash image URL with resize parameters."""
    return f"https://images.unsplash.com/photo-{photo_id}?w=800&h=600&fit=crop&q=80"


async def seed_images():
    """Add Unsplash images to items that have no media."""
    import asyncpg

    dsn = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(dsn)

    # Get items without media
    rows = await conn.fetch("""
        SELECT i.id, i.name, i.category
        FROM bh_item i
        WHERE i.id NOT IN (SELECT DISTINCT item_id FROM bh_item_media)
        ORDER BY i.category, i.name
    """)
    logger.info(f"Found {len(rows)} items without images")

    if not rows:
        logger.info("All items have images. Nothing to do.")
        await conn.close()
        return

    # Group by category for photo rotation
    by_category = {}
    for row in rows:
        cat = row["category"] or "other"
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(row)

    logger.info(f"Categories: {', '.join(f'{k}({len(v)})' for k, v in sorted(by_category.items()))}")

    added = 0
    for cat, items in by_category.items():
        photos = CATEGORY_PHOTOS.get(cat, DEFAULT_PHOTOS)
        for i, item in enumerate(items):
            photo_id = photos[i % len(photos)]
            url = unsplash_url(photo_id)
            alt_text = f"{item['name']} - product photo"

            await conn.execute("""
                INSERT INTO bh_item_media (id, item_id, media_type, url, alt_text, sort_order, created_at, updated_at)
                VALUES ($1, $2, 'PHOTO', $3, $4, 0, NOW(), NOW())
            """, uuid.uuid4(), item["id"], url, alt_text)
            added += 1

        logger.info(f"  {cat}: {len(items)} items -> {len(photos)} photos (rotating)")

    await conn.close()
    logger.info(f"DONE: {added} images added to {len(rows)} items")


if __name__ == "__main__":
    asyncio.run(seed_images())
