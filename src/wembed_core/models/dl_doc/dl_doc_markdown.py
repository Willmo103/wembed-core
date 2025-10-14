"""
wembed_core.models.dl_doc_markdown
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for doc_markdown.
"""

from datetime import datetime, timezone
from typing import List, Optional

from docling_core.transforms.chunker.base import BaseChunk, BaseMeta
from docling_core.types.doc.document import DoclingDocument
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class DLMarkdown(AppBase):
    """
    SQLAlchemy model for document markdown.
    Attributes:
      id (int): Unique identifier for the markdown.
      document_id (int): Foreign key referencing the associated document.
      markdown (Optional[str]): The markdown content of the document.
      created_at (datetime): Timestamp when the markdown was created.
      updated_at (datetime): Timestamp when the markdown was last updated.
    """

    __tablename__ = "dl_markdown"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("dl_doc.id"), nullable=False, index=True
    )
    markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
