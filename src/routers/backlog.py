"""Unified Backlog -- API + HTML routes.

Auth: BorrowHood cookie auth (bh_session). No separate login/callback per module.
No HelixApplication filtering -- single app.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_current_user_token, require_auth
from src.i18n import detect_language, get_translator, SUPPORTED_LANGUAGES
from src.models.backlog import (
    BHBacklogItem, BacklogItemType, BacklogStatus, BacklogPriority,
    BHBacklogActivity, BacklogActivityType,
)
from src.schemas.backlog import (
    BacklogItemCreate, BacklogItemUpdate, BacklogItemRead,
    BacklogActivityRead, BacklogSummary,
)

logger = logging.getLogger("bh.backlog_router")

# ================================================================
# Router Setup
# ================================================================
router = APIRouter(prefix="/api/v1/backlog", tags=["Backlog"])
html_router = APIRouter(tags=["Backlog - Web UI"])
templates = Jinja2Templates(directory="src/templates")


def _ctx(request: Request, token: Optional[dict] = None, **kwargs) -> dict:
    """Build template context with i18n."""
    query_lang = request.query_params.get("lang")
    cookie_lang = request.cookies.get("bh_lang")
    accept_lang = request.headers.get("accept-language")
    lang = detect_language(query_lang, cookie_lang, accept_lang)
    t = get_translator(lang)
    set_lang_cookie = query_lang and query_lang != cookie_lang
    ctx = {
        "request": request,
        "user": token,
        "t": t,
        "lang": lang,
        "supported_languages": SUPPORTED_LANGUAGES,
        "_set_lang_cookie": set_lang_cookie,
    }
    ctx.update(kwargs)
    return ctx


def _render(template_name: str, ctx: dict, status_code: int = 200):
    set_cookie = ctx.pop("_set_lang_cookie", False)
    lang = ctx.get("lang", "en")
    response = templates.TemplateResponse(template_name, ctx, status_code=status_code)
    if set_cookie:
        response.set_cookie("bh_lang", lang, max_age=365 * 24 * 3600, samesite="lax")
    return response


# ================================================================
# HTML: Board Page
# ================================================================
@html_router.get("/backlog", response_class=HTMLResponse)
async def backlog_board(
    request: Request,
    token: dict = Depends(require_auth),
):
    """Render the backlog board. Requires auth."""
    ctx = _ctx(request, token)
    return _render("pages/backlog.html", ctx)


# ================================================================
# API: Summary
# ================================================================
@router.get("/summary", response_model=BacklogSummary)
async def get_summary(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Backlog overview counts by status, type, priority."""
    status_result = await db.execute(
        select(
            BHBacklogItem.status,
            func.count().label("cnt"),
        ).group_by(BHBacklogItem.status)
    )
    status_counts = {row.status.value: row.cnt for row in status_result}

    type_result = await db.execute(
        select(
            BHBacklogItem.item_type,
            func.count().label("cnt"),
        ).group_by(BHBacklogItem.item_type)
    )
    type_counts = {row.item_type.value: row.cnt for row in type_result}

    priority_result = await db.execute(
        select(
            BHBacklogItem.priority,
            func.count().label("cnt"),
        ).group_by(BHBacklogItem.priority)
    )
    priority_counts = {row.priority.value: row.cnt for row in priority_result}

    total = sum(status_counts.values())

    return BacklogSummary(
        total=total,
        pending=status_counts.get("pending", 0),
        in_progress=status_counts.get("in_progress", 0),
        on_hold=status_counts.get("on_hold", 0),
        blocked=status_counts.get("blocked", 0),
        done=status_counts.get("done", 0),
        archived=status_counts.get("archived", 0),
        by_type=type_counts,
        by_priority=priority_counts,
    )


# ================================================================
# API: List Items
# ================================================================
@router.get("/items", response_model=list[BacklogItemRead])
async def list_items(
    item_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[str] = None,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List backlog items with optional filters."""
    query = select(BHBacklogItem)

    if item_type:
        try:
            t = BacklogItemType(item_type)
            query = query.where(BHBacklogItem.item_type == t)
        except ValueError:
            pass

    if status_filter:
        try:
            s = BacklogStatus(status_filter)
            query = query.where(BHBacklogItem.status == s)
        except ValueError:
            pass

    if priority:
        try:
            p = BacklogPriority(priority)
            query = query.where(BHBacklogItem.priority == p)
        except ValueError:
            pass

    if assigned_to:
        query = query.where(BHBacklogItem.assigned_to == assigned_to)

    query = query.order_by(BHBacklogItem.item_number)
    result = await db.execute(query)
    return result.scalars().all()


# ================================================================
# API: Create Item
# ================================================================
@router.post("/items", response_model=BacklogItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: BacklogItemCreate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Create a new backlog item."""
    max_num = await db.execute(
        select(func.coalesce(func.max(BHBacklogItem.item_number), 0))
    )
    next_number = max_num.scalar() + 1

    new_item = BHBacklogItem(
        item_number=next_number,
        title=item.title,
        description=item.description,
        item_type=item.item_type,
        priority=item.priority,
        assigned_to=item.assigned_to,
        due_date=item.due_date,
        estimated_hours=item.estimated_hours,
        tags=item.tags,
        created_by=item.created_by,
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)

    logger.info(f"BL-{next_number:03d} created: {item.title}")
    return new_item


# ================================================================
# API: User Feedback (public -- no auth required)
# ================================================================
from pydantic import BaseModel as _BaseModel, Field as _Field


class FeedbackCreate(_BaseModel):
    message: str = _Field(..., min_length=5, max_length=2000)
    page_url: str = _Field(..., max_length=500)
    feedback_type: str = _Field(default="bug", max_length=20)  # bug, idea, other
    email: Optional[str] = _Field(None, max_length=200)


@router.post("/feedback", status_code=201)
async def submit_feedback(
    data: FeedbackCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    token: Optional[dict] = Depends(get_current_user_token),
):
    """Submit user feedback -- creates a backlog item tagged 'user-feedback'.

    Works for both logged-in and anonymous users.
    Rate limited by IP via the global rate limiter.
    """
    # Determine who submitted
    submitter = "Anonymous"
    if token:
        from src.dependencies import get_user
        try:
            user = await get_user(db, token)
            submitter = user.display_name or user.username or user.email
        except Exception:
            pass
    elif data.email:
        submitter = data.email

    # Map feedback type to backlog type + priority
    type_map = {
        "bug": (BacklogItemType.BUG_FIX, BacklogPriority.HIGH),
        "idea": (BacklogItemType.FEATURE, BacklogPriority.MEDIUM),
        "other": (BacklogItemType.IMPROVEMENT, BacklogPriority.MEDIUM),
    }
    item_type, priority = type_map.get(data.feedback_type, (BacklogItemType.BUG_FIX, BacklogPriority.MEDIUM))

    # Auto-generate title from message
    title = data.message[:80].strip()
    if len(data.message) > 80:
        title = title.rsplit(" ", 1)[0] + "..."

    # Build description with context
    description = (
        f"**User Feedback**\n\n"
        f"{data.message}\n\n"
        f"---\n"
        f"- **Page:** {data.page_url}\n"
        f"- **Type:** {data.feedback_type}\n"
        f"- **From:** {submitter}\n"
        f"- **Browser:** {request.headers.get('user-agent', 'unknown')[:100]}\n"
    )

    max_num = await db.execute(
        select(func.coalesce(func.max(BHBacklogItem.item_number), 0))
    )
    next_number = max_num.scalar() + 1

    new_item = BHBacklogItem(
        item_number=next_number,
        title=f"[Feedback] {title}",
        description=description,
        item_type=item_type,
        priority=priority,
        tags="user-feedback",
        created_by=submitter,
    )
    db.add(new_item)
    await db.commit()

    logger.info(f"BL-{next_number:03d} feedback from {submitter}: {title}")
    return {"detail": "Feedback received", "item_number": next_number}


# ================================================================
# API: Get Single Item
# ================================================================
@router.get("/items/{item_id}", response_model=BacklogItemRead)
async def get_item(
    item_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get a single backlog item."""
    result = await db.execute(
        select(BHBacklogItem).where(BHBacklogItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Backlog item not found")
    return item


# ================================================================
# API: Update Item
# ================================================================
@router.put("/items/{item_id}", response_model=BacklogItemRead)
async def update_item(
    item_id: UUID,
    update: BacklogItemUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update a backlog item -- auto-creates activity log entries."""
    result = await db.execute(
        select(BHBacklogItem).where(BHBacklogItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Backlog item not found")

    actor = update.actor or "Angel"
    activities = []

    if update.status is not None and update.status != item.status:
        activities.append(BHBacklogActivity(
            item_id=item.id,
            activity_type=BacklogActivityType.STATUS_CHANGE,
            actor=actor,
            old_value=item.status.value,
            new_value=update.status.value,
        ))
        item.status = update.status

    if update.priority is not None and update.priority != item.priority:
        activities.append(BHBacklogActivity(
            item_id=item.id,
            activity_type=BacklogActivityType.PRIORITY_CHANGE,
            actor=actor,
            old_value=item.priority.value,
            new_value=update.priority.value,
        ))
        item.priority = update.priority

    if update.assigned_to is not None and update.assigned_to != (item.assigned_to or ""):
        new_assignee = update.assigned_to if update.assigned_to else None
        activities.append(BHBacklogActivity(
            item_id=item.id,
            activity_type=BacklogActivityType.ASSIGNED,
            actor=actor,
            old_value=item.assigned_to,
            new_value=new_assignee,
        ))
        item.assigned_to = new_assignee

    if update.comment:
        activities.append(BHBacklogActivity(
            item_id=item.id,
            activity_type=BacklogActivityType.COMMENT,
            actor=actor,
            comment=update.comment,
        ))

    if update.title is not None:
        item.title = update.title
    if update.description is not None:
        item.description = update.description
    if update.item_type is not None:
        item.item_type = update.item_type
    if update.due_date is not None:
        item.due_date = update.due_date
    if update.estimated_hours is not None:
        item.estimated_hours = update.estimated_hours
    if update.blocked_reason is not None:
        item.blocked_reason = update.blocked_reason if update.blocked_reason else None
    if update.tags is not None:
        item.tags = update.tags if update.tags else None

    for activity in activities:
        db.add(activity)

    await db.commit()
    await db.refresh(item)

    if activities:
        logger.info(f"BL-{item.item_number:03d} updated by {actor}: {len(activities)} activity entries")

    return item


# ================================================================
# API: Delete Item (soft delete -> archived)
# ================================================================
@router.delete("/items/{item_id}", status_code=status.HTTP_200_OK)
async def delete_item(
    item_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Soft delete a backlog item (set status=archived)."""
    result = await db.execute(
        select(BHBacklogItem).where(BHBacklogItem.id == item_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Backlog item not found")

    old_status = item.status.value
    item.status = BacklogStatus.ARCHIVED

    db.add(BHBacklogActivity(
        item_id=item.id,
        activity_type=BacklogActivityType.STATUS_CHANGE,
        actor="System",
        old_value=old_status,
        new_value=BacklogStatus.ARCHIVED.value,
    ))

    await db.commit()
    logger.info(f"BL-{item.item_number:03d} archived")
    return {"message": f"BL-{item.item_number:03d} archived"}


# ================================================================
# API: Item Activities
# ================================================================
@router.get("/items/{item_id}/activities", response_model=list[BacklogActivityRead])
async def get_item_activities(
    item_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get the activity log for a backlog item."""
    item_result = await db.execute(
        select(BHBacklogItem).where(BHBacklogItem.id == item_id)
    )
    if not item_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Backlog item not found")

    result = await db.execute(
        select(BHBacklogActivity)
        .where(BHBacklogActivity.item_id == item_id)
        .order_by(BHBacklogActivity.created_at.desc())
    )
    return result.scalars().all()
