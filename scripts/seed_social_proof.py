"""Bulk seed social-proof data: reviews, help posts, mentorships.

Run inside the Hetzner container:
    docker exec -it borrowhood python3 /app/scripts/seed_social_proof.py

Idempotent: skips rentals that already have reviews, skips existing mentorships,
and caps new help posts at a target count so re-runs don't blow up the board.

Targets:
  - ~120 reviews total on completed rentals (from current 16)
  - ~35 help posts total (from current 9) + realistic reply threads
  - 6 canonical Season 1 mentorships (from 0)
"""
import asyncio
import random
import sys
from datetime import datetime, timedelta, timezone
from uuid import UUID

sys.path.insert(0, "/app")


# ── Review content pools ───────────────────────────────────────────────

REVIEW_BODIES_5 = [
    "Absolutely perfect. Item was exactly as described, owner was responsive and friendly. Would rent again in a heartbeat.",
    "Five stars all the way. Pickup was smooth, the tool worked flawlessly, and returning was just as easy. Great neighbor!",
    "Couldn't be happier. Clean, well-maintained, and ready to go. This is what community sharing should feel like.",
    "Top-tier experience. Owner even threw in a few tips on how to use it properly. Saved me a ton vs buying.",
    "Fast, friendly, fair. The item did exactly what I needed. Will definitely come back for future projects.",
    "Worth every euro. Quality gear, quality person. BorrowHood at its best.",
    "Flawless transaction. Great communication before, during, and after. Highly recommend.",
    "This is the third time I've borrowed from this owner — never disappoints. Trusted source.",
    "Showed up on time, item was spotless, instructions were clear. 10/10.",
    "Made my weekend project possible. Without this rental I would've spent 3x buying new. Grazie mille!",
    "Honest, kind, and organized. Exactly the kind of people who make this platform work.",
    "Item in better condition than expected. Bonus points for the extra accessories included.",
    "Super easy process. Booked, picked up, used, returned. No drama.",
    "Owner was patient explaining how it works since I'd never used one. Above and beyond.",
]

REVIEW_BODIES_4 = [
    "Great experience overall. Small delay at pickup but nothing major. Item worked perfectly.",
    "Very good. One minor scuff but otherwise exactly what I needed. Would rent again.",
    "Solid. Would have been 5 stars if pickup location was a bit easier to find.",
    "Really happy with the rental. Item did the job, owner was friendly. Small nit: manual was in Italian only.",
    "Good gear, good person. Minor cosmetic wear but fully functional.",
    "Did what I needed. Owner was communicative. Nothing to complain about.",
    "Happy customer. Would've liked a quick tutorial but figured it out from YouTube.",
    "Reliable. Showed up, worked, returned. Simple and effective.",
]

REVIEW_BODIES_3 = [
    "Decent. Item worked but was a bit more worn than the photos suggested.",
    "Okay experience. Communication could have been faster.",
]

REVIEW_TITLES = [
    "Would rent again!", "Great neighbor, great tool", "Perfect for my project",
    "Exactly what I needed", "Highly recommend", "Smooth as butter",
    "Top-notch experience", "Trusted local", "Saved my weekend",
    "Community at its best", "10/10", "Fair and friendly", None, None, None,
]

# ── Help Board post pool ────────────────────────────────────────────────

HELP_POSTS = [
    # NEED posts
    ("need", "tools", "low", "Need to borrow a stud finder for 1 hour",
     "Hanging some heavy shelves this weekend. Would love to borrow a stud finder so I don't Swiss-cheese my wall. Trapani center, can pick up."),
    ("need", "cooking", "normal", "Looking for a pasta machine this Saturday",
     "Nonna is visiting from Palermo and we want to make fresh tagliatelle together. Anyone in the Erice area willing to lend one for a day?"),
    ("need", "transport", "urgent", "Help! Dead car battery, need jumper cables",
     "Car won't start, parked near Piazza Vittorio Emanuele. Phone at 40%. Anyone nearby with jumpers? Will bring coffee."),
    ("need", "gardening", "normal", "Hedge trimmer for an afternoon",
     "The rosemary hedge has officially eaten my walkway. Gas or electric both work. Can pick up after work."),
    ("need", "repair", "normal", "Sewing machine for one zipper repair",
     "Favorite jacket zipper gave out. One 10-minute repair. I'll sew you something small in return if you want."),
    ("need", "learning", "low", "Anyone willing to teach me sourdough basics?",
     "Tired of buying bread. I'll bring the flour and the wine. Just need someone patient to walk me through a first loaf."),
    ("need", "kids", "normal", "Bouncy castle for Sunday birthday party",
     "Little one turns 6 this weekend. Looking to borrow or rent for a few hours. Backyard in Paceco."),
    ("need", "moving", "urgent", "Help moving a fridge across town -- tomorrow",
     "New apartment, old fridge still works but I can't carry it alone. Need 1-2 strong hands + a van or trailer. Can pay for gas + pizza."),
    ("need", "tech", "low", "Old printer for one 30-page document",
     "Don't own one, don't want to own one, but need to print contracts. Can I drop by and print?"),
    ("need", "photography", "normal", "Tripod for real estate photos tomorrow",
     "Agent asked me to shoot a listing. My tripod broke. Any photographers in Trapani willing to lend for 3 hours?"),
    ("need", "outdoor", "normal", "Camping tent for 2 people, one weekend",
     "Planning a trip to Zingaro reserve. Sleeping bags sorted, need a tent for Saturday night."),
    ("need", "music", "low", "Acoustic guitar to practice for a week",
     "Kids want to learn, but I don't want to commit to buying one yet. Happy to rent or trade a skill."),
    ("need", "repair", "urgent", "Plumber's snake -- kitchen sink won't drain",
     "Drain totally clogged. Would love to borrow a drain snake for an hour before water overflows."),
    # OFFER posts
    ("offer", "teaching", "normal", "Free beginner welding lesson in my garage",
     "I've got the gear, the space, and the patience. If you've ever wanted to weld a simple bracket, come by on a Saturday. Bring safety glasses."),
    ("offer", "cooking", "normal", "Sunday sauce -- come help, take home a jar",
     "Making 10 liters of tomato sauce this Sunday. Four hands better than two. Come help peel, stir, jar -- leave with 2 liters."),
    ("offer", "transport", "low", "Driving to Palermo Friday -- empty van",
     "Heading to Palermo Friday morning, returning Saturday. If anyone needs something moved or delivered, say the word."),
    ("offer", "kids", "normal", "Free kids' bike helmet (size M)",
     "Outgrew it. Barely used. First kid who needs it, it's yours. Trapani pickup."),
    ("offer", "repair", "normal", "Fix your bike chain, free",
     "I love fixing bikes. If your chain is rusty, stretched, or snapped, bring it by. Small repairs on the spot."),
    ("offer", "gardening", "low", "Free basil seedlings -- 20 plants",
     "Grew way too many. Twenty baby basil plants looking for a good home. Come grab a few."),
    ("offer", "outdoor", "normal", "Fishing rods + tackle, free borrow",
     "Going anywhere along the coast? I have two rods + a tackle box collecting dust. Take them for the day."),
    ("offer", "learning", "normal", "Teach a kid to read a map, free",
     "Screens are rotting the whole next generation's sense of direction. If your kid is 8+, I'll take them on a compass walk for an hour."),
    ("offer", "tools", "normal", "Full woodworking bench available weekends",
     "My garage has a proper workbench, vices, clamps, hand tools. Come use it any Saturday. Just clean up after yourself."),
    ("offer", "cooking", "low", "Extra pizza dough every Thursday",
     "I make 5 kg of dough weekly for family pizza night. Always have extra. Come grab a ball, free."),
    ("offer", "tech", "normal", "Set up your grandma's phone, free",
     "I'll install WhatsApp, show her how to video call, add your number to favorites. One hour, zero euros. Grandmas deserve it."),
    ("offer", "photography", "normal", "Free family portraits at San Vito beach",
     "Practicing portraits. Looking for 3 families to shoot in April. Free digital copies, nice location."),
]

HELP_REPLIES = [
    "I have one you can borrow -- DM me, I'm 5 min from center.",
    "Got two actually. Bring them back whenever.",
    "Happy to help. Free tomorrow morning, does that work?",
    "Count me in. I'll message you privately.",
    "Have one gathering dust. Yours for the weekend.",
    "Saw this earlier -- someone beat me to it? Let me know if you still need.",
    "Sending my number over DM. Stay put, on my way.",
    "Mine's older but works. No rush returning it.",
    "I'm in Paceco -- too far? Happy to drive in.",
    "Used to do this for a living. I'll teach you properly. No charge.",
    "Grazie for organizing this. This is exactly why I joined the platform.",
    "Available Saturday if the offer still stands.",
    "Beautiful. This is the spirit.",
    "I can bring a second person + tools. Let's do it.",
    "Message me -- I've got what you need and some spare time.",
]


# ── Canonical Season 1 mentorships ─────────────────────────────────────

CANONICAL_MENTORSHIPS = [
    # (mentor_email, apprentice_email, type, skill, category, goal, status)
    ("sally@borrowhood.local", "sofiaferretti@borrowhood.local",
     "mentor", "Sourdough & pastry baking", "cooking",
     "Sofia bakes her own Christmas cookies for the family by December",
     "active", 14, 3),
    ("pietro@borrowhood.local", "sofiaferretti@borrowhood.local",
     "apprentice", "Drone flying & aerial photography", "photography",
     "Solo certification flight over Erice by summer",
     "active", 22, 5),
    ("john@borrowhood.local", "sofiaferretti@borrowhood.local",
     "intern", "Delivery operations & customer care", "transport",
     "Complete 20 delivery shifts and earn first paycheck",
     "active", 40, 8),
    ("leonardo@borrowhood.local", "sofiaferretti@borrowhood.local",
     "mentor", "Workshop safety & hand tool basics", "repair",
     "Build a small birdhouse start to finish solo",
     "active", 8, 2),
    ("mike@borrowhood.local", "nicolo@borrowhood.local",
     "mentor", "Welding fundamentals", "repair",
     "Weld a trailer hitch that passes the load test",
     "active", 12, 3),
    ("angel@borrowhood.local", "anne@borrowhood.local",
     "mentor", "QA testing & bug reporting", "tech",
     "Anne writes her first 50 BorrowHood bug reports with clear repro steps",
     "completed", 60, 10),
]


# ── Helpers ─────────────────────────────────────────────────────────────

TIER_WEIGHTS = {
    "newcomer": 1.0, "active": 2.0, "trusted": 5.0, "pillar": 8.0, "legend": 10.0,
}


def pick_review_content(rating: int):
    if rating == 5:
        body = random.choice(REVIEW_BODIES_5)
    elif rating == 4:
        body = random.choice(REVIEW_BODIES_4)
    else:
        body = random.choice(REVIEW_BODIES_3)
    title = random.choice(REVIEW_TITLES)
    return title, body


def random_sub_rating(overall: int) -> int:
    """Sub-ratings usually match overall ± 1."""
    roll = random.random()
    if roll < 0.7:
        return overall
    if roll < 0.9:
        return max(1, overall - 1)
    return min(5, overall + 1) if overall < 5 else overall


async def seed_reviews(db, target_total: int = 120):
    from sqlalchemy import select, func
    from src.models.rental import BHRental, RentalStatus
    from src.models.listing import BHListing
    from src.models.item import BHItem
    from src.models.review import BHReview
    from src.models.user import BHUser

    existing_count = await db.scalar(select(func.count(BHReview.id)))
    needed = max(0, target_total - existing_count)
    print(f"[reviews] existing={existing_count}, target={target_total}, needed={needed}")
    if needed == 0:
        return 0

    # Rentals that are completed-ish and don't have a review yet
    reviewed_rental_ids = set(
        (await db.execute(select(BHReview.rental_id))).scalars().all()
    )

    q = (
        select(BHRental, BHListing, BHItem)
        .join(BHListing, BHRental.listing_id == BHListing.id)
        .join(BHItem, BHListing.item_id == BHItem.id)
        .where(BHRental.status.in_([
            RentalStatus.COMPLETED, RentalStatus.PAYMENT_CONFIRMED,
            RentalStatus.RETURNED, RentalStatus.PICKED_UP,
        ]))
    )
    rows = (await db.execute(q)).all()
    eligible = [r for r in rows if r[0].id not in reviewed_rental_ids]
    print(f"[reviews] eligible rentals without review: {len(eligible)}")
    if not eligible:
        return 0

    random.shuffle(eligible)
    created = 0
    for rental, listing, item in eligible[:needed]:
        reviewer = await db.scalar(select(BHUser).where(BHUser.id == rental.renter_id))
        reviewee = await db.scalar(select(BHUser).where(BHUser.id == item.owner_id))
        if not reviewer or not reviewee:
            continue

        # 75% five-star, 20% four-star, 5% three-star
        roll = random.random()
        rating = 5 if roll < 0.75 else (4 if roll < 0.95 else 3)
        title, body = pick_review_content(rating)

        tier = reviewer.badge_tier.value if reviewer.badge_tier else "newcomer"
        weight = TIER_WEIGHTS.get(tier, 1.0)

        # Reviewed within last 60 days, anchored after rental end
        anchor = rental.actual_return or rental.requested_end or rental.updated_at or datetime.now(timezone.utc)
        if anchor.tzinfo is None:
            anchor = anchor.replace(tzinfo=timezone.utc)
        offset_days = random.randint(1, 14)
        reviewed_at = min(anchor + timedelta(days=offset_days), datetime.now(timezone.utc))

        review = BHReview(
            rental_id=rental.id,
            reviewer_id=reviewer.id,
            reviewee_id=reviewee.id,
            rating=rating,
            title=title,
            body=body,
            rating_accuracy=random_sub_rating(rating),
            rating_communication=random_sub_rating(rating),
            rating_value=random_sub_rating(rating),
            rating_timeliness=random_sub_rating(rating),
            would_recommend=rating >= 4,
            reviewer_tier=tier,
            weight=weight,
            helpful_count=random.choices([0, 0, 0, 1, 2, 3, 5], k=1)[0],
            visible=True,
            content_language="en",
            created_at=reviewed_at,
            updated_at=reviewed_at,
        )
        db.add(review)
        created += 1

    await db.flush()
    print(f"[reviews] created {created}")
    return created


async def seed_help_posts(db, target_total: int = 35):
    from sqlalchemy import select, func
    from src.models.helpboard import BHHelpPost, BHHelpReply, HelpType, HelpStatus, HelpUrgency
    from src.models.user import BHUser

    existing_count = await db.scalar(select(func.count(BHHelpPost.id)))
    needed = max(0, target_total - existing_count)
    print(f"[help] existing={existing_count}, target={target_total}, needed={needed}")
    if needed == 0:
        return 0

    # Pick from demo cast only (keeps it canonical)
    demo_emails = [
        "angel@borrowhood.local", "leonardo@borrowhood.local", "sally@borrowhood.local",
        "mike@borrowhood.local", "marco@borrowhood.local", "pietro@borrowhood.local",
        "jake@borrowhood.local", "john@borrowhood.local", "maria@borrowhood.local",
        "sofiaferretti@borrowhood.local", "rosa@borrowhood.local", "anne@borrowhood.local",
        "nicolo@borrowhood.local", "nino@borrowhood.local",
    ]
    users = (await db.execute(
        select(BHUser).where(BHUser.email.in_(demo_emails)).where(BHUser.deleted_at.is_(None))
    )).scalars().all()
    if len(users) < 3:
        print(f"[help] too few demo users ({len(users)}) -- skipping")
        return 0

    pool = HELP_POSTS[:needed]
    created = 0
    for help_type, category, urgency, title, body in pool:
        author = random.choice(users)
        status = random.choices(
            [HelpStatus.OPEN, HelpStatus.IN_PROGRESS, HelpStatus.RESOLVED],
            weights=[0.5, 0.2, 0.3], k=1,
        )[0]
        created_at = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 21))
        post = BHHelpPost(
            author_id=author.id,
            help_type=HelpType(help_type),
            status=status,
            urgency=HelpUrgency(urgency),
            title=title,
            body=body,
            category=category,
            content_language="en",
            neighborhood=random.choice(["Trapani centro", "Erice", "Paceco", "San Vito", None]),
            upvote_count=random.choices([0, 1, 2, 3, 5, 8], k=1)[0],
            created_at=created_at,
            updated_at=created_at,
        )
        db.add(post)
        await db.flush()

        # 1-4 replies per post
        reply_count = random.choices([1, 2, 3, 4], weights=[0.2, 0.4, 0.3, 0.1], k=1)[0]
        repliers = random.sample([u for u in users if u.id != author.id], min(reply_count, len(users) - 1))
        for replier in repliers:
            reply_at = created_at + timedelta(hours=random.randint(1, 48))
            db.add(BHHelpReply(
                post_id=post.id,
                author_id=replier.id,
                body=random.choice(HELP_REPLIES),
                upvote_count=random.choices([0, 0, 1, 2], k=1)[0],
                created_at=reply_at,
                updated_at=reply_at,
            ))
        post.reply_count = len(repliers)
        if status == HelpStatus.RESOLVED and repliers:
            post.resolved_by_id = repliers[0].id
        created += 1

    await db.flush()
    print(f"[help] created {created} posts + replies")
    return created


async def seed_mentorships(db):
    from sqlalchemy import select, func
    from src.models.mentorship import BHMentorship, MentorshipType, MentorshipStatus
    from src.models.user import BHUser

    existing = await db.scalar(select(func.count(BHMentorship.id)))
    print(f"[mentorships] existing={existing}")
    if existing >= len(CANONICAL_MENTORSHIPS):
        return 0

    created = 0
    for (mentor_email, apprentice_email, m_type, skill, category,
         goal, status, hours, milestones) in CANONICAL_MENTORSHIPS:
        mentor = await db.scalar(select(BHUser).where(BHUser.email == mentor_email))
        apprentice = await db.scalar(select(BHUser).where(BHUser.email == apprentice_email))
        if not mentor or not apprentice:
            print(f"[mentorships] skip: missing {mentor_email} or {apprentice_email}")
            continue

        dup = await db.scalar(
            select(BHMentorship.id)
            .where(BHMentorship.mentor_id == mentor.id)
            .where(BHMentorship.apprentice_id == apprentice.id)
            .where(BHMentorship.skill_name == skill)
        )
        if dup:
            continue

        started = datetime.now(timezone.utc) - timedelta(days=random.randint(30, 120))
        db.add(BHMentorship(
            mentor_id=mentor.id,
            apprentice_id=apprentice.id,
            mentorship_type=MentorshipType(m_type),
            status=MentorshipStatus(status),
            skill_name=skill,
            skill_category=category,
            hours_logged=hours,
            milestones_completed=milestones,
            goal=goal,
            notes="Seeded canonical Season 1 arc.",
            created_at=started,
            updated_at=started,
        ))
        created += 1

    await db.flush()
    print(f"[mentorships] created {created}")
    return created


async def rebuild_user_points(db):
    """Recount reviews_given / reviews_received / total_points after seeding."""
    from sqlalchemy import select, func
    from src.models.review import BHReview
    from src.models.user import BHUser, BHUserPoints

    users = (await db.execute(select(BHUser).where(BHUser.deleted_at.is_(None)))).scalars().all()
    updated = 0
    for u in users:
        given = await db.scalar(
            select(func.count(BHReview.id)).where(BHReview.reviewer_id == u.id)
        )
        received = await db.scalar(
            select(func.count(BHReview.id)).where(BHReview.reviewee_id == u.id)
        )
        points_row = await db.scalar(
            select(BHUserPoints).where(BHUserPoints.user_id == u.id)
        )
        if not points_row:
            points_row = BHUserPoints(user_id=u.id, total_points=0)
            db.add(points_row)

        points_row.reviews_given = given
        points_row.reviews_received = received
        # Light points bump so leaderboard shifts
        points_row.total_points = (
            (points_row.rentals_completed or 0) * 10
            + given * 5
            + received * 3
        )
        updated += 1

    await db.flush()
    print(f"[points] recomputed for {updated} users")
    return updated


async def main():
    from src.database import async_session

    random.seed(42)  # reproducible-ish

    async with async_session() as db:
        r = await seed_reviews(db)
        h = await seed_help_posts(db)
        m = await seed_mentorships(db)
        p = await rebuild_user_points(db)
        await db.commit()
        print()
        print(f"DONE: reviews+{r}, help_posts+{h}, mentorships+{m}, points_rebuilt={p}")


if __name__ == "__main__":
    asyncio.run(main())
