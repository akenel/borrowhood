"""Content translation model -- v1 schema placeholder for v2 translation engine.

See CONCEPT.md: "ContentTranslation table exists from v1 -- empty, ready for v2."
Translation is done on DISPLAY, not on storage. The original text is sacred.
"""

import enum
from typing import Optional
import uuid

from sqlalchemy import Enum as SQLEnum, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base, BHBase


class TranslationSource(str, enum.Enum):
    BROWSER = "browser"
    API = "api"
    USER = "user"
    AI = "ai"


class BHContentTranslation(BHBase, Base):
    """Cached translation of user-generated content.

    v1: Table created but empty. Schema ready for v2 LibreTranslate integration.
    v2: Server-side translation with caching (translate once, serve forever).
    v3: 65+ languages, AI-powered context-aware translation.
    """

    __tablename__ = "bh_content_translation"

    content_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
    )  # "item_description", "item_story", "review", "comment"
    content_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, index=True,
    )
    source_language: Mapped[str] = mapped_column(String(10), nullable=False)  # "it", "en"
    target_language: Mapped[str] = mapped_column(String(10), nullable=False)  # "en", "it"
    translated_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_by: Mapped[TranslationSource] = mapped_column(
        SQLEnum(TranslationSource, name="bh_translation_source",
                values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
