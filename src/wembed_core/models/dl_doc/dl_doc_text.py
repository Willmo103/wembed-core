"""
wembed_core.models.dl_doc_text
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for doc_text.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class DLText(AppBase):
    """
    SQLAlchemy model for document text.
    Attributes:
      id (int): Unique identifier for the text.
      document_id (int): Foreign key referencing the associated document.
      text (Optional[str]): The text content of the document.
      created_at (datetime): Timestamp when the text was created.
      updated_at (datetime): Timestamp when the text was last updated.
    """

    __tablename__ = "dl_text"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("dl_doc.id"), nullable=False, index=True
    )
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True, index=True)
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
