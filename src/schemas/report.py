"""Pydantic schemas for content moderation reports."""

from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from src.models.report import ReportReason, ReportStatus


class ReportCreate(BaseModel):
    entity_type: str = Field(..., pattern="^(item|review|user)$")
    entity_id: UUID
    reason: ReportReason
    detail: Optional[str] = Field(None, max_length=1000)


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reporter_id: UUID
    entity_type: str
    entity_id: UUID
    reason: ReportReason
    detail: Optional[str] = None
    status: ReportStatus
    created_at: datetime
