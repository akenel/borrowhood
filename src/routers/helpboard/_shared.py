"""Shared helpers and constants for helpboard/ package."""
from pathlib import Path

from sqlalchemy.orm import selectinload

from src.models.helpboard import BHHelpPost, BHHelpReply

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "uploads" / "helpboard"

# ── Helpers ──

def _enrich_post(post: BHHelpPost, user_upvoted: bool = False) -> dict:
    """Convert a post ORM object to enriched dict for HelpPostOut."""
    d = {
        "id": post.id,
        "author_id": post.author_id,
        "help_type": post.help_type,
        "status": post.status,
        "urgency": post.urgency,
        "title": post.title,
        "body": post.body,
        "category": post.category,
        "content_language": post.content_language,
        "neighborhood": post.neighborhood,
        "item_id": post.item_id,
        "resolved_by_id": post.resolved_by_id,
        "reply_count": post.reply_count,
        "upvote_count": post.upvote_count,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "author_name": post.author.display_name if post.author else None,
        "author_slug": post.author.slug if post.author else None,
        "author_avatar": post.author.avatar_url if post.author else None,
        "resolved_by_name": post.resolved_by.display_name if post.resolved_by else None,
        "item_name": post.item.name if post.item else None,
        "item_slug": str(post.item.id) if post.item else None,
        "media": post.media if post.media else [],
        "user_upvoted": user_upvoted,
    }
    return d


def _enrich_reply(reply: BHHelpReply) -> dict:
    """Convert a reply ORM object to enriched dict for HelpReplyOut."""
    return {
        "id": reply.id,
        "post_id": reply.post_id,
        "author_id": reply.author_id,
        "body": reply.body,
        "parent_reply_id": reply.parent_reply_id,
        "upvote_count": reply.upvote_count,
        "created_at": reply.created_at,
        "updated_at": reply.updated_at,
        "author_name": reply.author.display_name if reply.author else None,
        "author_slug": reply.author.slug if reply.author else None,
        "author_avatar": reply.author.avatar_url if reply.author else None,
        "media": reply.media if reply.media else [],
        "children": [],
    }


def _build_reply_tree(flat_replies: list[BHHelpReply]) -> list[dict]:
    """Build threaded reply tree from flat list."""
    by_id = {}
    roots = []
    for r in flat_replies:
        enriched = _enrich_reply(r)
        by_id[r.id] = enriched

    for r in flat_replies:
        enriched = by_id[r.id]
        if r.parent_reply_id and r.parent_reply_id in by_id:
            by_id[r.parent_reply_id]["children"].append(enriched)
        else:
            roots.append(enriched)
    return roots


POST_EAGER = [
    selectinload(BHHelpPost.author),
    selectinload(BHHelpPost.resolved_by),
    selectinload(BHHelpPost.item),
    selectinload(BHHelpPost.media),
]


