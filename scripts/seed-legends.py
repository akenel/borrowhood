"""Seed additional legendary users into BorrowHood."""
import json
import asyncio
import sys

sys.path.insert(0, "/app")


async def seed_legends():
    from sqlalchemy import select
    from src.database import async_session
    from src.models.user import (
        BHUser, BHUserLanguage, BHUserSkill, BHUserPoints,
        BadgeTier, WorkshopType, CEFRLevel,
    )

    with open("/app/seed_data/legends-100.json") as f:
        data = json.load(f)

    cefr_values = [e.value for e in CEFRLevel]

    async with async_session() as db:
        created = 0
        skipped = 0
        for u in data["users"]:
            slug = u["slug"]
            existing = await db.scalar(select(BHUser.id).where(BHUser.slug == slug))
            if existing:
                skipped += 1
                continue

            wt = u.get("workshop_type")
            user = BHUser(
                keycloak_id="seed-" + slug,
                email=u["email"],
                display_name=u["display_name"],
                slug=slug,
                workshop_name=u.get("workshop_name"),
                workshop_type=WorkshopType(wt) if wt else None,
                tagline=u.get("tagline"),
                bio=u.get("bio"),
                city=u.get("city"),
                country_code=u.get("country_code"),
                latitude=u.get("latitude"),
                longitude=u.get("longitude"),
                badge_tier=BadgeTier(u.get("badge_tier", "newcomer")),
                offers_delivery=u.get("offers_delivery", False),
                offers_pickup=u.get("offers_pickup", False),
                offers_training=u.get("offers_training", False),
                offers_custom_orders=u.get("offers_custom_orders", False),
                offers_repair=u.get("offers_repair", False),
            )
            db.add(user)
            await db.flush()

            for lang in u.get("languages", []):
                prof = lang["proficiency"]
                db.add(BHUserLanguage(
                    user_id=user.id,
                    language_code=lang["language_code"],
                    proficiency=CEFRLevel(prof) if prof in cefr_values else CEFRLevel.B2,
                ))

            for skill in u.get("skills", []):
                db.add(BHUserSkill(
                    user_id=user.id,
                    skill_name=skill["skill_name"],
                    category=skill["category"],
                    self_rating=skill.get("self_rating", 3),
                    years_experience=skill.get("years_experience"),
                ))

            pts = u.get("points", {})
            if pts:
                db.add(BHUserPoints(
                    user_id=user.id,
                    total_points=pts.get("total_points", 0),
                    rentals_completed=pts.get("rentals_completed", 0),
                    reviews_given=pts.get("reviews_given", 0),
                    reviews_received=pts.get("reviews_received", 0),
                    items_listed=pts.get("items_listed", 0),
                    giveaways_completed=pts.get("giveaways_completed", 0),
                ))

            created += 1

        await db.commit()
        print(f"Created: {created}, Skipped: {skipped}")


asyncio.run(seed_legends())
