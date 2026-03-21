"""Help Board API -- community requests, offers, threaded replies, media.

Public reads, auth-gated writes. Media uploads stored on local disk
(static/uploads/helpboard/) -- 10MB max, photos + videos.
"""

import uuid as uuid_mod
from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, File, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, get_user, require_auth

from src.models.helpboard import (
    ALLOWED_MEDIA_TYPES, ALLOWED_IMAGE_TYPES, MAX_MEDIA_SIZE,
    BHHelpPost, BHHelpReply, BHHelpMedia, BHHelpUpvote,
    HelpMediaType, HelpStatus, HelpType,
)
from src.models.item import BHItem
from src.models.user import BHUser
from src.schemas.helpboard import (
    HelpPostCreate, HelpPostOut, HelpPostUpdate, HelpMediaOut,
    HelpReplyCreate, HelpReplyOut, HelpReplyUpdate, PaginatedPosts, ResolvePost,
    HelpDraftRequest, HelpDraftResponse,
)

router = APIRouter(prefix="/api/v1/helpboard", tags=["helpboard"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads" / "helpboard"


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


# ── Posts ──

@router.get("/posts", response_model=PaginatedPosts)
async def list_posts(
    help_type: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    item_id: Optional[UUID] = None,
    q: Optional[str] = None,
    sort: str = Query("newest", pattern="^(newest|oldest|most_replies|urgent_first|most_upvoted)$"),
    limit: int = Query(12, ge=1, le=100),
    offset: int = Query(0, ge=0),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """List help posts with optional filters, search, and sort. Public endpoint."""
    base = select(BHHelpPost).where(BHHelpPost.deleted_at.is_(None))

    if help_type:
        try:
            base = base.where(BHHelpPost.help_type == HelpType(help_type))
        except ValueError:
            pass
    if category:
        base = base.where(BHHelpPost.category == category)
    if status_filter:
        try:
            base = base.where(BHHelpPost.status == HelpStatus(status_filter))
        except ValueError:
            pass
    if item_id:
        base = base.where(BHHelpPost.item_id == item_id)
    if q:
        search_term = f"%{q}%"
        base = base.where(
            BHHelpPost.title.ilike(search_term) | BHHelpPost.body.ilike(search_term)
        )

    # Total count with same filters (before limit/offset)
    count_query = select(func.count()).select_from(base.subquery())
    total = await db.scalar(count_query) or 0

    # Sorting
    if sort == "oldest":
        base = base.order_by(BHHelpPost.created_at.asc())
    elif sort == "most_replies":
        base = base.order_by(BHHelpPost.reply_count.desc(), BHHelpPost.created_at.desc())
    elif sort == "most_upvoted":
        base = base.order_by(BHHelpPost.upvote_count.desc(), BHHelpPost.created_at.desc())
    elif sort == "urgent_first":
        from sqlalchemy import case
        urgency_order = case(
            (BHHelpPost.urgency == "urgent", 0),
            (BHHelpPost.urgency == "normal", 1),
            (BHHelpPost.urgency == "low", 2),
            else_=3,
        )
        base = base.order_by(urgency_order, BHHelpPost.created_at.desc())
    else:  # newest (default)
        base = base.order_by(BHHelpPost.created_at.desc())

    base = base.options(*POST_EAGER).offset(offset).limit(limit)
    result = await db.execute(base)
    posts = result.scalars().unique().all()

    # Check user upvotes if authenticated
    user_upvoted_ids = set()
    try:
        token = await get_current_user_token(request) if request else None
        if token:
            user = await get_user(db, token)
            if user and posts:
                post_ids = [p.id for p in posts]
                uv_result = await db.execute(
                    select(BHHelpUpvote.post_id).where(
                        BHHelpUpvote.user_id == user.id,
                        BHHelpUpvote.post_id.in_(post_ids),
                    )
                )
                user_upvoted_ids = {row[0] for row in uv_result.all()}
    except Exception:
        pass

    items = [_enrich_post(p, user_upvoted=p.id in user_upvoted_ids) for p in posts]

    return PaginatedPosts(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
        has_more=offset + limit < total,
    )


@router.get("/posts/{post_id}")
async def get_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single help post with enriched data."""
    result = await db.execute(
        select(BHHelpPost)
        .where(BHHelpPost.id == post_id, BHHelpPost.deleted_at.is_(None))
        .options(*POST_EAGER)
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return _enrich_post(post)


@router.post("/posts", response_model=HelpPostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: HelpPostCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create a help request or offer. Optionally tag an item."""
    user = await get_user(db, token)

    # Validate item_id if provided
    if data.item_id:
        item_result = await db.execute(
            select(BHItem).where(BHItem.id == data.item_id, BHItem.deleted_at.is_(None))
        )
        if not item_result.scalars().first():
            raise HTTPException(status_code=400, detail="Tagged item not found")

    post = BHHelpPost(
        author_id=user.id,
        help_type=data.help_type,
        title=data.title,
        body=data.body,
        category=data.category,
        urgency=data.urgency,
        neighborhood=data.neighborhood,
        content_language=data.content_language,
        item_id=data.item_id,
    )
    db.add(post)
    await db.commit()

    # Reload with relationships
    result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post.id).options(*POST_EAGER)
    )
    post = result.scalars().first()
    return _enrich_post(post)


@router.patch("/posts/{post_id}", response_model=HelpPostOut)
async def update_post(
    post_id: UUID,
    data: HelpPostUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Edit a help post. Author only. Can't edit resolved/closed posts."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post_id, BHHelpPost.deleted_at.is_(None))
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Only the author can edit")
    if post.status in (HelpStatus.RESOLVED, HelpStatus.CLOSED):
        raise HTTPException(status_code=400, detail="Cannot edit resolved or closed posts")

    if data.title is not None:
        post.title = data.title
    if data.body is not None:
        post.body = data.body
    if data.category is not None:
        post.category = data.category
    if data.urgency is not None:
        post.urgency = data.urgency
    if data.neighborhood is not None:
        post.neighborhood = data.neighborhood
    if data.item_id is not None:
        # Validate item
        item_result = await db.execute(
            select(BHItem).where(BHItem.id == data.item_id, BHItem.deleted_at.is_(None))
        )
        if not item_result.scalars().first():
            raise HTTPException(status_code=400, detail="Tagged item not found")
        post.item_id = data.item_id

    await db.commit()
    result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post.id).options(*POST_EAGER)
    )
    post = result.scalars().first()
    return _enrich_post(post)


@router.post("/draft", response_model=HelpDraftResponse)
async def ai_draft_post(
    data: HelpDraftRequest,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """AI-assisted help post drafting. User describes their situation in a few words,
    AI writes the full post, estimates value, and suggests next steps.

    This is the feature that would have saved Johnny from giving his bike away.
    """
    from src.services.gemini import helpboard_draft
    from src.models.item import BHItem

    # Find similar items for context
    similar = []
    words = data.description.lower().split()
    for word in words[:3]:
        if len(word) > 2:
            stmt = select(BHItem).where(
                BHItem.name.ilike(f"%{word}%"), BHItem.deleted_at.is_(None)
            ).limit(5)
            result = await db.execute(stmt)
            for item in result.scalars():
                similar.append({
                    "name": item.name,
                    "category": item.category,
                    "price": 0,
                })

    ai_result, provider = await helpboard_draft(
        description=data.description,
        help_type=data.help_type.value,
        language=data.language,
        similar_items=similar if similar else None,
    )

    if ai_result:
        return HelpDraftResponse(
            title=ai_result.get("title", ""),
            body=ai_result.get("body", ""),
            category=ai_result.get("category", "hand_tools"),
            urgency=ai_result.get("urgency", "normal"),
            estimated_value=float(ai_result.get("estimated_value", 0)) if ai_result.get("estimated_value") else None,
            value_explanation=ai_result.get("value_explanation", ""),
            suggestions=ai_result.get("suggestions", []),
            ai_provider=provider,
        )

    # All AI failed -- basic template fallback
    return HelpDraftResponse(
        title=data.description[:200],
        body=f"I {'need help with' if data.help_type.value == 'need' else 'can help with'}: {data.description}",
        category="hand_tools",
        urgency="normal",
        suggestions=["Add more details about your situation", "Tag a specific item if relevant", "Check if someone already offers this on the Browse page"],
        ai_provider="template",
    )


@router.patch("/posts/{post_id}/status")
async def update_post_status(
    post_id: UUID,
    new_status: str,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update post status. Author only."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post_id, BHHelpPost.deleted_at.is_(None))
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Only the author can update status")
    try:
        post.status = HelpStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")
    await db.commit()
    return {"status": post.status.value}


# ── Resolve ──

@router.post("/posts/{post_id}/resolve")
async def resolve_post(
    post_id: UUID,
    data: ResolvePost,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Mark a post as resolved. Author picks who helped (or self-resolves)."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post_id, BHHelpPost.deleted_at.is_(None))
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Only the author can resolve")

    post.status = HelpStatus.RESOLVED
    if data.resolved_by_id:
        # Validate the resolver exists
        resolver = await db.execute(select(BHUser).where(BHUser.id == data.resolved_by_id))
        if not resolver.scalars().first():
            raise HTTPException(status_code=400, detail="Resolver user not found")
        post.resolved_by_id = data.resolved_by_id

        # Notify the resolver
        from src.models.notification import NotificationType
        from src.services.notify import create_notification
        await create_notification(
            db=db,
            user_id=data.resolved_by_id,
            notification_type=NotificationType.SYSTEM,
            title=f"{user.display_name} marked you as the helper on: {post.title}",
            link="/helpboard",
            entity_type="helpboard",
            entity_id=post.id,
        )
    else:
        post.resolved_by_id = user.id  # self-resolve

    await db.commit()
    return {"status": "resolved", "resolved_by_id": str(post.resolved_by_id)}


# ── Upvote ──

@router.post("/posts/{post_id}/upvote")
async def toggle_upvote(
    post_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Toggle upvote on a post. Upvote if not yet, remove if already upvoted."""
    user = await get_user(db, token)

    # Verify post exists
    post_result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post_id, BHHelpPost.deleted_at.is_(None))
    )
    post = post_result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Check existing upvote
    existing = await db.execute(
        select(BHHelpUpvote).where(
            BHHelpUpvote.post_id == post_id,
            BHHelpUpvote.user_id == user.id,
        )
    )
    vote = existing.scalars().first()

    if vote:
        await db.delete(vote)
        post.upvote_count = max(0, post.upvote_count - 1)
        action = "removed"
    else:
        db.add(BHHelpUpvote(post_id=post_id, user_id=user.id))
        post.upvote_count += 1
        action = "upvoted"

    await db.commit()
    return {"action": action, "upvote_count": post.upvote_count}


# ── Replies (threaded) ──

@router.get("/posts/{post_id}/replies")
async def list_replies(post_id: UUID, db: AsyncSession = Depends(get_db)):
    """List replies for a post as a threaded tree. Public endpoint."""
    result = await db.execute(
        select(BHHelpReply)
        .where(BHHelpReply.post_id == post_id, BHHelpReply.deleted_at.is_(None))
        .options(selectinload(BHHelpReply.author), selectinload(BHHelpReply.media))
        .order_by(BHHelpReply.created_at.asc())
    )
    flat = result.scalars().unique().all()
    return _build_reply_tree(flat)


@router.post("/posts/{post_id}/replies", status_code=status.HTTP_201_CREATED)
async def create_reply(
    post_id: UUID,
    data: HelpReplyCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Reply to a help post. Set parent_reply_id for threading."""
    user = await get_user(db, token)

    # Verify post exists
    post_result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post_id, BHHelpPost.deleted_at.is_(None))
    )
    post = post_result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Validate parent reply if threading
    if data.parent_reply_id:
        parent_result = await db.execute(
            select(BHHelpReply).where(
                BHHelpReply.id == data.parent_reply_id,
                BHHelpReply.post_id == post_id,
                BHHelpReply.deleted_at.is_(None),
            )
        )
        if not parent_result.scalars().first():
            raise HTTPException(status_code=400, detail="Parent reply not found in this post")

    reply = BHHelpReply(
        post_id=post_id,
        author_id=user.id,
        body=data.body,
        parent_reply_id=data.parent_reply_id,
    )
    db.add(reply)
    post.reply_count += 1
    await db.flush()

    # Notify the post author (unless replying to own post)
    if post.author_id != user.id:
        from src.models.notification import NotificationType
        from src.services.notify import create_notification
        await create_notification(
            db=db,
            user_id=post.author_id,
            notification_type=NotificationType.SYSTEM,
            title=f"{user.display_name} replied to your post: {post.title}",
            link="/helpboard",
            entity_type="helpboard",
            entity_id=post.id,
        )

    # If threading, also notify the parent reply author
    if data.parent_reply_id:
        parent_result = await db.execute(
            select(BHHelpReply).where(BHHelpReply.id == data.parent_reply_id)
        )
        parent_reply = parent_result.scalars().first()
        if parent_reply and parent_reply.author_id != user.id and parent_reply.author_id != post.author_id:
            from src.models.notification import NotificationType
            from src.services.notify import create_notification
            await create_notification(
                db=db,
                user_id=parent_reply.author_id,
                notification_type=NotificationType.SYSTEM,
                title=f"{user.display_name} replied to your comment on: {post.title}",
                link="/helpboard",
                entity_type="helpboard",
                entity_id=post.id,
            )

    await db.commit()

    # Reload with relationships
    result = await db.execute(
        select(BHHelpReply).where(BHHelpReply.id == reply.id)
        .options(selectinload(BHHelpReply.author), selectinload(BHHelpReply.media))
    )
    reply = result.scalars().first()
    return _enrich_reply(reply)


# ── Media Upload ──

@router.post("/posts/{post_id}/media", response_model=HelpMediaOut, status_code=status.HTTP_201_CREATED)
async def upload_post_media(
    post_id: UUID,
    file: UploadFile = File(...),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload a photo or video (max 10MB) to a help post. Author only."""
    user = await get_user(db, token)

    # Verify post exists and user is author
    result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post_id, BHHelpPost.deleted_at.is_(None))
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != user.id:
        raise HTTPException(status_code=403, detail="Only the author can upload media")

    media = await _save_media(file, user.id, db, post_id=post_id)
    return media


@router.patch("/replies/{reply_id}", response_model=HelpReplyOut)
async def update_reply(
    reply_id: UUID,
    data: HelpReplyUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Edit a reply. Author only."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHHelpReply)
        .options(selectinload(BHHelpReply.author), selectinload(BHHelpReply.media))
        .where(BHHelpReply.id == reply_id, BHHelpReply.deleted_at.is_(None))
    )
    reply = result.scalars().first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    if reply.author_id != user.id:
        raise HTTPException(status_code=403, detail="Only the author can edit")
    reply.body = data.body
    await db.commit()
    await db.refresh(reply)
    return _enrich_reply(reply)


@router.delete("/replies/{reply_id}", status_code=204)
async def delete_reply(
    reply_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a reply. Author only."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHHelpReply).where(BHHelpReply.id == reply_id, BHHelpReply.deleted_at.is_(None))
    )
    reply = result.scalars().first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    if reply.author_id != user.id:
        raise HTTPException(status_code=403, detail="Only the author can delete")
    from datetime import datetime, timezone
    reply.deleted_at = datetime.now(timezone.utc)
    # Decrement reply count on post
    post_result = await db.execute(select(BHHelpPost).where(BHHelpPost.id == reply.post_id))
    post = post_result.scalars().first()
    if post and post.reply_count > 0:
        post.reply_count -= 1
    await db.commit()


@router.post("/replies/{reply_id}/media", response_model=HelpMediaOut, status_code=status.HTTP_201_CREATED)
async def upload_reply_media(
    reply_id: UUID,
    file: UploadFile = File(...),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Upload a photo or video (max 10MB) to a reply. Author only."""
    user = await get_user(db, token)

    # Verify reply exists and user is author
    result = await db.execute(
        select(BHHelpReply).where(BHHelpReply.id == reply_id, BHHelpReply.deleted_at.is_(None))
    )
    reply = result.scalars().first()
    if not reply:
        raise HTTPException(status_code=404, detail="Reply not found")
    if reply.author_id != user.id:
        raise HTTPException(status_code=403, detail="Only the author can upload media")

    media = await _save_media(file, user.id, db, reply_id=reply_id)
    return media


@router.delete("/media/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Delete a media attachment. Author only."""
    user = await get_user(db, token)
    result = await db.execute(
        select(BHHelpMedia).where(BHHelpMedia.id == media_id)
    )
    media = result.scalars().first()
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    if media.uploader_id != user.id:
        raise HTTPException(status_code=403, detail="Only the uploader can delete media")
    # Delete file from disk
    filepath = Path(media.url.lstrip("/"))
    if filepath.exists():
        filepath.unlink()
    await db.delete(media)
    await db.commit()


async def _save_media(
    file: UploadFile,
    uploader_id,
    db: AsyncSession,
    post_id: UUID = None,
    reply_id: UUID = None,
) -> BHHelpMedia:
    """Validate, save to disk, create DB record."""
    if file.content_type not in ALLOWED_MEDIA_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File must be an image (JPEG/PNG/WebP/GIF) or video (MP4/WebM/MOV). Got: {file.content_type}"
        )

    contents = await file.read()
    if len(contents) > MAX_MEDIA_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB)")

    # Determine type
    media_type = HelpMediaType.VIDEO if file.content_type in ALLOWED_IMAGE_TYPES.__class__() and file.content_type not in ALLOWED_IMAGE_TYPES else HelpMediaType.PHOTO
    if file.content_type.startswith("video/"):
        media_type = HelpMediaType.VIDEO
    else:
        media_type = HelpMediaType.PHOTO

    # Save to disk
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "bin"
    safe_exts = {"jpg", "jpeg", "png", "webp", "gif", "mp4", "webm", "mov"}
    if ext not in safe_exts:
        ext = "bin"
    filename = f"{uuid_mod.uuid4().hex}.{ext}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filepath = UPLOAD_DIR / filename
    filepath.write_bytes(contents)

    media = BHHelpMedia(
        post_id=post_id,
        reply_id=reply_id,
        uploader_id=uploader_id,
        media_type=media_type,
        url=f"/static/uploads/helpboard/{filename}",
        filename=file.filename or filename,
        file_size=len(contents),
        content_type=file.content_type,
        alt_text=None,
        sort_order=0,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    return media


# ── Summary ──

@router.get("/summary")
async def helpboard_summary(db: AsyncSession = Depends(get_db)):
    """Summary stats for the help board."""
    total = await db.scalar(
        select(func.count()).select_from(BHHelpPost).where(BHHelpPost.deleted_at.is_(None))
    )
    open_count = await db.scalar(
        select(func.count()).select_from(BHHelpPost).where(
            BHHelpPost.deleted_at.is_(None), BHHelpPost.status == HelpStatus.OPEN
        )
    )
    needs = await db.scalar(
        select(func.count()).select_from(BHHelpPost).where(
            BHHelpPost.deleted_at.is_(None), BHHelpPost.help_type == HelpType.NEED
        )
    )
    offers = await db.scalar(
        select(func.count()).select_from(BHHelpPost).where(
            BHHelpPost.deleted_at.is_(None), BHHelpPost.help_type == HelpType.OFFER
        )
    )
    resolved = await db.scalar(
        select(func.count()).select_from(BHHelpPost).where(
            BHHelpPost.deleted_at.is_(None), BHHelpPost.status == HelpStatus.RESOLVED
        )
    )
    return {
        "total": total or 0,
        "open": open_count or 0,
        "needs": needs or 0,
        "offers": offers or 0,
        "resolved": resolved or 0,
    }


# ── Posts by item (for item detail cross-link) ──

@router.get("/items/{item_id}/posts")
async def posts_for_item(
    item_id: UUID,
    limit: int = Query(5, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get help board posts tagged to a specific item. For item detail pages."""
    result = await db.execute(
        select(BHHelpPost)
        .where(BHHelpPost.item_id == item_id, BHHelpPost.deleted_at.is_(None))
        .options(*POST_EAGER)
        .order_by(BHHelpPost.created_at.desc())
        .limit(limit)
    )
    posts = result.scalars().unique().all()
    return [_enrich_post(p) for p in posts]
