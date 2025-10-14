"""
wembed_core.models.dl_doc_doctags
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for doc_doctags.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class DLDocTags(AppBase):
    """
    SQLAlchemy model for document tags.
    Attributes:
      id (int): Unique identifier for the tags.
      document_id (int): Foreign key referencing the associated document.
      tags (Optional[str]): The tags content of the document.
      created_at (datetime): Timestamp when the tags were created.
      updated_at (datetime): Timestamp when the tags were last updated.
    """

    __tablename__ = "dl_doc_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("dl_doc.id"), nullable=False, index=True
    )
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
