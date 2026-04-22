"""Unified Backlog -- API + HTML routes.

Auth: BorrowHood cookie auth (bh_session). No separate login/callback per module.
No HelixApplication filtering -- single app.
"""

import logging
import uuid as uuid_mod
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.database import get_db
from src.dependencies import get_current_user_token, require_auth
from src.i18n import detect_language, get_translator, SUPPORTED_LANGUAGES
from src.models.backlog import (
    ALLOWED_FEEDBACK_MIME_TYPES, MAX_FEEDBACK_FILE_SIZE,
    BHBacklogItem, BacklogItemType, BacklogStatus, BacklogPriority,
    BHBacklogActivity, BacklogActivityType,
    BHFeedbackMedia, FeedbackMediaType,
)
from src.schemas.backlog import (
    BacklogItemCreate, BacklogItemUpdate, BacklogItemRead,
    BacklogActivityRead, BacklogSummary, FeedbackMediaRead,
)

FEEDBACK_UPLOAD_DIR = Path(__file__).resolve().parent.parent / "static" / "uploads" / "feedback"
MAX_ATTACHMENTS_PER_ITEM = 5  # 3 user files + session_report + optional screen_capture
FEEDBACK_UPLOAD_WINDOW = timedelta(hours=1)

logger = logging.getLogger("bh.backlog_router")

# ================================================================
# Router Setup
# ================================================================
router = APIRouter(prefix="/api/v1/backlog", tags=["Backlog"])
html_router = APIRouter(tags=["Backlog - Web UI"])
templates = Jinja2Templates(directory="src/templates")
# base.html footer uses {{ now().year }} -- register the same Jinja globals
# the pages router exposes so shared templates don't blow up here.
templates.env.globals["now"] = lambda: datetime.now(timezone.utc)
templates.env.globals["now_utc"] = lambda: datetime.now(timezone.utc)


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
    return {"detail": "Feedback received", "item_number": next_number, "item_id": str(new_item.id)}


# ================================================================
# API: Feedback Media (attach to a recent feedback -- public)
# ================================================================
def _classify_media(mime: str) -> FeedbackMediaType:
    if mime == "application/json":
        return FeedbackMediaType.SESSION_REPORT
    if mime == "application/pdf":
        return FeedbackMediaType.DOCUMENT
    if mime.startswith("video/"):
        return FeedbackMediaType.VIDEO
    return FeedbackMediaType.IMAGE


_EXT_BY_MIME = {
    "image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "image/gif": "gif",
    "video/mp4": "mp4", "video/webm": "webm", "video/quicktime": "mov",
    "application/pdf": "pdf", "application/json": "json",
}


@router.post("/feedback/{item_number}/media", response_model=FeedbackMediaRead, status_code=201)
async def upload_feedback_media(
    item_number: int,
    file: UploadFile = File(...),
    kind: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    token: Optional[dict] = Depends(get_current_user_token),
):
    """Attach a file to a feedback backlog item.

    Public (no auth). Only allowed within FEEDBACK_UPLOAD_WINDOW of item creation
    and capped at MAX_ATTACHMENTS_PER_ITEM files per item to prevent drive-by abuse.
    """
    if file.content_type not in ALLOWED_FEEDBACK_MIME_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported type: {file.content_type}")

    item = (await db.execute(
        select(BHBacklogItem).where(BHBacklogItem.item_number == item_number)
    )).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Feedback item not found")

    if "user-feedback" not in (item.tags or ""):
        raise HTTPException(status_code=400, detail="Not a user-feedback item")

    age = datetime.now(timezone.utc) - item.created_at
    if age > FEEDBACK_UPLOAD_WINDOW:
        raise HTTPException(status_code=410, detail="Upload window closed (1 hour after submission)")

    existing = (await db.execute(
        select(func.count()).select_from(BHFeedbackMedia).where(BHFeedbackMedia.item_id == item.id)
    )).scalar()
    if existing >= MAX_ATTACHMENTS_PER_ITEM:
        raise HTTPException(status_code=409, detail="Attachment limit reached")

    contents = await file.read()
    if len(contents) > MAX_FEEDBACK_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB)")

    if kind == "screen_capture":
        media_type = FeedbackMediaType.SCREEN_CAPTURE
    else:
        media_type = _classify_media(file.content_type)

    ext = _EXT_BY_MIME.get(file.content_type, "bin")
    filename = f"{uuid_mod.uuid4().hex}.{ext}"
    FEEDBACK_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (FEEDBACK_UPLOAD_DIR / filename).write_bytes(contents)

    uploader = item.created_by
    if token:
        try:
            from src.dependencies import get_user as _gu
            u = await _gu(db, token)
            uploader = u.display_name or u.username or uploader
        except Exception:
            pass

    media = BHFeedbackMedia(
        item_id=item.id,
        media_type=media_type,
        url=f"/static/uploads/feedback/{filename}",
        filename=file.filename or filename,
        mime_type=file.content_type,
        file_size=len(contents),
        uploader=uploader,
    )
    db.add(media)
    await db.commit()
    await db.refresh(media)
    logger.info(f"BL-{item.item_number:03d} attachment: {media_type.value} ({len(contents)} bytes)")
    return media


@router.get("/items/{item_id}/media", response_model=list[FeedbackMediaRead])
async def list_item_media(
    item_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List all media attachments on a backlog item."""
    result = await db.execute(
        select(BHFeedbackMedia)
        .where(BHFeedbackMedia.item_id == item_id)
        .order_by(BHFeedbackMedia.created_at.asc())
    )
    return result.scalars().all()


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
