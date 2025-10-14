"""
wembed_core.models.dl_doc_html
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for doc_html.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class DLHtml(AppBase):
    """
    SQLAlchemy model for document HTML.
    Attributes:
      id (int): Unique identifier for the HTML.
      document_id (int): Foreign key referencing the associated document.
      html (Optional[str]): The HTML content of the document.
      created_at (datetime): Timestamp when the HTML was created.
      updated_at (datetime): Timestamp when the HTML was last updated.
    """

    __tablename__ = "dl_html"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("dl_doc.id"), nullable=False, index=True
    )
    html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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
