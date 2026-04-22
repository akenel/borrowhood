"""Help post CRUD: list, get, create, update, status, resolve, AI draft, suggested helpers."""

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

from ._shared import UPLOAD_DIR, POST_EAGER, _enrich_post, _enrich_reply, _build_reply_tree

router = APIRouter()

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


# ── Smart Matching: Suggested Helpers ──

@router.get("/posts/{post_id}/suggested-helpers")
async def suggested_helpers(
    post_id: UUID,
    limit: int = 5,
    db: AsyncSession = Depends(get_db),
):
    """Find users with skills matching this help post's category.

    Public endpoint -- no auth required so visitors can see who can help.
    Returns up to `limit` users ranked by verified skills, rating, trust.
    """
    result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post_id, BHHelpPost.deleted_at.is_(None))
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    from src.services.helpboard_matching import find_suggested_helpers
    helpers = await find_suggested_helpers(
        db=db,
        post_category=post.category,
        post_author_id=post.author_id,
        limit=min(limit, 10),
    )
    return helpers


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



