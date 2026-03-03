"""Notification API.

In-app notifications with read/unread tracking.
All endpoints require authentication.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.dependencies import get_user, require_auth
from src.models.notification import BHNotification, NotificationType
from src.models.notification_pref import BHNotificationPref
from src.models.user import BHUser

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


class NotificationOut(BaseModel):
    id: UUID
    notification_type: NotificationType
    title: str
    body: str | None = None
    link: str | None = None
    read: bool
    created_at: str

    class Config:
        from_attributes = True


class NotificationSummary(BaseModel):
    total: int
    unread: int


@router.get("/summary", response_model=NotificationSummary)
async def notification_summary(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get notification counts (total + unread) for the bell icon."""
    user = await get_user(db, token)

    total = await db.scalar(
        select(func.count(BHNotification.id))
        .where(BHNotification.user_id == user.id)
    ) or 0

    unread = await db.scalar(
        select(func.count(BHNotification.id))
        .where(BHNotification.user_id == user.id)
        .where(BHNotification.read == False)
    ) or 0

    return {"total": total, "unread": unread}


@router.get("", response_model=List[NotificationOut])
async def list_notifications(
    unread_only: bool = False,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """List notifications for the authenticated user."""
    user = await get_user(db, token)

    query = (
        select(BHNotification)
        .where(BHNotification.user_id == user.id)
    )

    if unread_only:
        query = query.where(BHNotification.read == False)

    query = query.order_by(BHNotification.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    notifications = result.scalars().all()

    # Convert datetime to string for serialization
    out = []
    for n in notifications:
        out.append(NotificationOut(
            id=n.id,
            notification_type=n.notification_type,
            title=n.title,
            body=n.body,
            link=n.link,
            read=n.read,
            created_at=n.created_at.isoformat(),
        ))
    return out


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: UUID,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Mark a single notification as read."""
    user = await get_user(db, token)

    result = await db.execute(
        select(BHNotification)
        .where(BHNotification.id == notification_id)
        .where(BHNotification.user_id == user.id)
    )
    notification = result.scalars().first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.read = True
    await db.commit()
    return {"status": "ok"}


@router.post("/read-all")
async def mark_all_read(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Mark all notifications as read."""
    user = await get_user(db, token)

    await db.execute(
        update(BHNotification)
        .where(BHNotification.user_id == user.id)
        .where(BHNotification.read == False)
        .values(read=True)
    )
    await db.commit()
    return {"status": "ok"}


# --- Notification Preferences ---

class PrefItem(BaseModel):
    notification_type: str
    enabled: bool


class PrefUpdate(BaseModel):
    preferences: List[PrefItem]


@router.get("/preferences")
async def get_notification_preferences(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get notification preferences for the authenticated user.

    Returns all notification types with their enabled status.
    Types not explicitly set default to True (enabled).
    """
    user = await get_user(db, token)

    # Fetch user's overrides
    result = await db.execute(
        select(BHNotificationPref)
        .where(BHNotificationPref.user_id == user.id)
    )
    overrides = {p.notification_type: p.enabled for p in result.scalars().all()}

    # Build full list with defaults
    prefs = []
    for nt in NotificationType:
        prefs.append({
            "notification_type": nt.value,
            "enabled": overrides.get(nt.value, True),
        })

    return {
        "notify_telegram": user.notify_telegram,
        "notify_email": user.notify_email,
        "preferences": prefs,
    }


@router.put("/preferences")
async def update_notification_preferences(
    body: PrefUpdate,
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Update per-type notification preferences.

    Only types included in the request body are updated.
    """
    user = await get_user(db, token)

    valid_types = {nt.value for nt in NotificationType}

    for item in body.preferences:
        if item.notification_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid notification type: {item.notification_type}",
            )

        # Upsert: check if pref exists
        existing = await db.scalar(
            select(BHNotificationPref.id)
            .where(BHNotificationPref.user_id == user.id)
            .where(BHNotificationPref.notification_type == item.notification_type)
        )

        if existing:
            await db.execute(
                update(BHNotificationPref)
                .where(BHNotificationPref.id == existing)
                .values(enabled=item.enabled)
            )
        else:
            db.add(BHNotificationPref(
                user_id=user.id,
                notification_type=item.notification_type,
                enabled=item.enabled,
            ))

    await db.commit()
    return {"status": "ok", "updated": len(body.preferences)}
