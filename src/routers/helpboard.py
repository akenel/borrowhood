"""Help Board API -- community requests and offers.

Public reads, auth-gated writes.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import require_auth
from src.models.helpboard import BHHelpPost, BHHelpReply, HelpStatus, HelpType
from src.models.user import BHUser
from src.schemas.helpboard import HelpPostCreate, HelpPostOut, HelpReplyCreate, HelpReplyOut

router = APIRouter(prefix="/api/v1/helpboard", tags=["helpboard"])


async def _get_user(db: AsyncSession, keycloak_id: str) -> BHUser:
    result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == keycloak_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="User not provisioned")
    return user


@router.get("/posts", response_model=list[HelpPostOut])
async def list_posts(
    help_type: Optional[str] = None,
    category: Optional[str] = None,
    status_filter: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List help posts with optional filters. Public endpoint."""
    query = select(BHHelpPost).where(BHHelpPost.deleted_at.is_(None))

    if help_type:
        try:
            query = query.where(BHHelpPost.help_type == HelpType(help_type))
        except ValueError:
            pass
    if category:
        query = query.where(BHHelpPost.category == category)
    if status_filter:
        try:
            query = query.where(BHHelpPost.status == HelpStatus(status_filter))
        except ValueError:
            pass

    query = query.order_by(BHHelpPost.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/posts/{post_id}", response_model=HelpPostOut)
async def get_post(post_id: UUID, db: AsyncSession = Depends(get_db)):
    """Get a single help post."""
    result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post_id, BHHelpPost.deleted_at.is_(None))
    )
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/posts", response_model=HelpPostOut, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: HelpPostCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create a help request or offer."""
    user = await _get_user(db, token["sub"])
    post = BHHelpPost(
        author_id=user.id,
        help_type=data.help_type,
        title=data.title,
        body=data.body,
        category=data.category,
        urgency=data.urgency,
        neighborhood=data.neighborhood,
        content_language=data.content_language,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return post


@router.patch("/posts/{post_id}/status")
async def update_post_status(
    post_id: UUID,
    new_status: str,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update post status. Author only."""
    user = await _get_user(db, token["sub"])
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


@router.get("/posts/{post_id}/replies", response_model=list[HelpReplyOut])
async def list_replies(post_id: UUID, db: AsyncSession = Depends(get_db)):
    """List replies for a post. Public endpoint."""
    result = await db.execute(
        select(BHHelpReply)
        .where(BHHelpReply.post_id == post_id, BHHelpReply.deleted_at.is_(None))
        .order_by(BHHelpReply.created_at.asc())
    )
    return result.scalars().all()


@router.post("/posts/{post_id}/replies", response_model=HelpReplyOut, status_code=status.HTTP_201_CREATED)
async def create_reply(
    post_id: UUID,
    data: HelpReplyCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Reply to a help post."""
    user = await _get_user(db, token["sub"])

    # Verify post exists
    post_result = await db.execute(
        select(BHHelpPost).where(BHHelpPost.id == post_id, BHHelpPost.deleted_at.is_(None))
    )
    post = post_result.scalars().first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    reply = BHHelpReply(
        post_id=post_id,
        author_id=user.id,
        body=data.body,
    )
    db.add(reply)
    post.reply_count += 1
    await db.commit()
    await db.refresh(reply)
    return reply


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
    return {
        "total": total or 0,
        "open": open_count or 0,
        "needs": needs or 0,
        "offers": offers or 0,
    }
