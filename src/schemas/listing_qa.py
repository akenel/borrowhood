from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class QACreate(BaseModel):
    listing_id: UUID
    question: str = Field(..., min_length=5, max_length=2000)


class QAAnswer(BaseModel):
    answer: str = Field(..., min_length=1, max_length=5000)


class QAOut(BaseModel):
    id: UUID
    listing_id: UUID
    asker_id: UUID
    question: str
    answer: Optional[str] = None
    answered_by_id: Optional[UUID] = None
    answered_at: Optional[datetime] = None
    created_at: datetime
    asker_name: Optional[str] = None
    asker_avatar: Optional[str] = None
    answerer_name: Optional[str] = None

    class Config:
        from_attributes = True
