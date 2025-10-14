"""
wembed_core.models.dl_doc_json
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for doc_json.
"""

from datetime import datetime, timezone
from typing import Optional

from docling_core.types.doc.document import DoclingDocument
from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class DLDoc(AppBase):
    """
    SQLAlchemy model for document.
    Attributes:
      id (int): Unique identifier for the document.
      document_id (int): Foreign key referencing the associated document.
      json (Optional[str]): The json content of the document.
      created_at (datetime): Timestamp when the document was created.
      updated_at (datetime): Timestamp when the document was last updated.
    """

    __tablename__ = "dl_doc"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doc_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
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

    def doc_json_validate(self) -> Optional[DoclingDocument]:
        """Return the document as a DoclingDocument object."""
        if self.doc_json:
            try:
                return DoclingDocument.model_validate_json(self.doc_json)
            except Exception:
                return None
        return None
