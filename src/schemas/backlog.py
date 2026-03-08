"""Pydantic schemas for Unified Backlog."""

from datetime import datetime, date
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from src.models.backlog import BacklogItemType, BacklogStatus, BacklogPriority


# ================================================================
# Backlog Item Schemas
# ================================================================
class BacklogItemCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    item_type: BacklogItemType = Field(default=BacklogItemType.DEV_TASK)
    priority: BacklogPriority = Field(default=BacklogPriority.MEDIUM)
    assigned_to: Optional[str] = Field(None, max_length=100)
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    tags: Optional[str] = Field(None, max_length=500)
    created_by: str = Field(default="Angel", min_length=1, max_length=100)


class BacklogItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    item_type: Optional[BacklogItemType] = None
    status: Optional[BacklogStatus] = None
    priority: Optional[BacklogPriority] = None
    assigned_to: Optional[str] = Field(None, max_length=100)
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    blocked_reason: Optional[str] = None
    tags: Optional[str] = Field(None, max_length=500)
    comment: Optional[str] = Field(None, min_length=1)
    actor: str = Field(default="Angel", min_length=1, max_length=100)


class BacklogItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    item_number: int
    item_type: BacklogItemType
    status: BacklogStatus
    priority: BacklogPriority
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    blocked_reason: Optional[str] = None
    tags: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: datetime


# ================================================================
# Activity Schemas
# ================================================================
class BacklogActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    item_id: UUID
    activity_type: str
    actor: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    comment: Optional[str] = None
    created_at: datetime


# ================================================================
# Summary
# ================================================================
class BacklogSummary(BaseModel):
    total: int
    pending: int
    in_progress: int
    on_hold: int
    blocked: int
    done: int
    archived: int
    by_type: dict[str, int] = {}
    by_priority: dict[str, int] = {}
