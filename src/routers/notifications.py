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
from src.dependencies import require_auth
from src.models.notification import BHNotification, NotificationType
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


async def _get_user(db: AsyncSession, keycloak_id: str) -> BHUser:
    result = await db.execute(
        select(BHUser).where(BHUser.keycloak_id == keycloak_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=403, detail="User not provisioned")
    return user


@router.get("/summary", response_model=NotificationSummary)
async def notification_summary(
    token: dict = Depends(require_auth),
    db: AsyncSession = Depends(get_db),
):
    """Get notification counts (total + unread) for the bell icon."""
    user = await _get_user(db, token["sub"])

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
    user = await _get_user(db, token["sub"])

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
    user = await _get_user(db, token["sub"])

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
    user = await _get_user(db, token["sub"])

    await db.execute(
        update(BHNotification)
        .where(BHNotification.user_id == user.id)
        .where(BHNotification.read == False)
        .values(read=True)
    )
    await db.commit()
    return {"status": "ok"}
