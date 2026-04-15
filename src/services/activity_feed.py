"""Live activity feed -- last N platform events for the homepage.

Pulls recent reviews, help posts/replies, mentorships, item listings, and
event RSVPs, merges by timestamp, returns a capped list of dicts
ready for the home template.
"""
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.helpboard import BHHelpPost, BHHelpReply
from src.models.item import BHItem
from src.models.mentorship import BHMentorship
from src.models.review import BHReview


def _avatar_for(user) -> str | None:
    if not user:
        return None
    return user.avatar_url or None


def _display(user) -> str:
    if not user:
        return "Someone"
    return user.display_name or user.slug or "Someone"


async def get_activity_feed(db: AsyncSession, limit: int = 10) -> list[dict[str, Any]]:
    """Return recent platform events for social-proof display."""
    per_source = max(3, limit)

    # 1. Recent reviews -- most valuable social proof
    review_rows = (await db.execute(
        select(BHReview)
        .options(
            selectinload(BHReview.reviewer),
            selectinload(BHReview.reviewee),
        )
        .where(BHReview.visible.is_(True))
        .order_by(BHReview.created_at.desc())
        .limit(per_source)
    )).scalars().all()

    # 2. Recent help posts
    help_rows = (await db.execute(
        select(BHHelpPost)
        .options(selectinload(BHHelpPost.author))
        .order_by(BHHelpPost.created_at.desc())
        .limit(per_source)
    )).scalars().all()

    # 3. Recent help replies (someone jumping in to help counts)
    reply_rows = (await db.execute(
        select(BHHelpReply)
        .options(
            selectinload(BHHelpReply.author),
            selectinload(BHHelpReply.post).selectinload(BHHelpPost.author),
        )
        .order_by(BHHelpReply.created_at.desc())
        .limit(per_source)
    )).scalars().all()

    # 4. Recent mentorships formed
    mentor_rows = (await db.execute(
        select(BHMentorship)
        .options(
            selectinload(BHMentorship.mentor),
            selectinload(BHMentorship.apprentice),
        )
        .order_by(BHMentorship.created_at.desc())
        .limit(per_source)
    )).scalars().all()

    # 5. Recently listed items
    item_rows = (await db.execute(
        select(BHItem)
        .options(selectinload(BHItem.owner))
        .where(BHItem.deleted_at.is_(None))
        .order_by(BHItem.created_at.desc())
        .limit(per_source)
    )).scalars().all()

    events: list[dict[str, Any]] = []

    for r in review_rows:
        stars = "⭐" * r.rating
        events.append({
            "kind": "review",
            "when": r.created_at,
            "icon": "star",
            "accent": "amber",
            "avatar": _avatar_for(r.reviewer),
            "actor": _display(r.reviewer),
            "verb": f"left a {stars} review for",
            "target": _display(r.reviewee),
            "target_href": f"/u/{r.reviewee.slug}" if r.reviewee and r.reviewee.slug else None,
        })

    for h in help_rows:
        verb = "asked for help" if h.help_type.value == "need" else "offered to help with"
        events.append({
            "kind": "help_post",
            "when": h.created_at,
            "icon": "hand",
            "accent": "emerald",
            "avatar": _avatar_for(h.author),
            "actor": _display(h.author),
            "verb": verb,
            "target": h.title,
            "target_href": "/helpboard",
        })

    for rep in reply_rows:
        post = rep.post
        if not post:
            continue
        events.append({
            "kind": "help_reply",
            "when": rep.created_at,
            "icon": "reply",
            "accent": "blue",
            "avatar": _avatar_for(rep.author),
            "actor": _display(rep.author),
            "verb": "replied to",
            "target": _display(post.author) + "'s post",
            "target_href": "/helpboard",
        })

    for m in mentor_rows:
        events.append({
            "kind": "mentorship",
            "when": m.created_at,
            "icon": "mentor",
            "accent": "purple",
            "avatar": _avatar_for(m.mentor),
            "actor": _display(m.mentor),
            "verb": f"is mentoring {_display(m.apprentice)} in",
            "target": m.skill_name,
            "target_href": None,
        })

    for it in item_rows:
        events.append({
            "kind": "item",
            "when": it.created_at,
            "icon": "plus",
            "accent": "indigo",
            "avatar": _avatar_for(it.owner),
            "actor": _display(it.owner),
            "verb": "listed",
            "target": it.name,
            "target_href": f"/items/{it.slug}" if it.slug else None,
        })

    # Merge -- newest first, cap
    events.sort(key=lambda e: e["when"] or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
    return events[:limit]
