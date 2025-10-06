"""
wembed_core.models.dl_documents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for documents.
"""

from datetime import datetime, timezone
from typing import List, Optional

from docling_core.transforms.chunker.base import BaseChunk
from docling_core.types.doc.document import DoclingDocument
from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import AppBase


class DLDocuments(AppBase):
    """
    SQLAlchemy model for documents.

    Attributes:
      id (int): Unique identifier for the document.
      source (str): The source of the document (e.g., file path, URL).
      source_type (str): The type of the source (e.g., 'file', 'url').
      source_ref (Optional[int]): Reference ID to another related entity (e.g., input ID).
      dl_doc (Optional[str]): The original document content in string format.
      markdown (Optional[str]): The document content in markdown format.
      html (Optional[str]): The document content in HTML format.
      text (Optional[str]): The plain text content of the document.
      doctags (Optional[str]): Any tags associated with the document.
      chunks_json (Optional[List[BaseChunk]]): List of chunks derived from the document.
      created_at (datetime): Timestamp when the document was created.
      updated_at (Optional[datetime]): Timestamp when the document was last updated.
    """

    __tablename__ = "dl_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    source_ref: Mapped[Optional[int]] = mapped_column(
        ForeignKey("dl_inputs.id"), nullable=True
    )
    dl_doc: Mapped[Optional[DoclingDocument]] = mapped_column(Text, nullable=True)
    markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    doctags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chunks_json: Mapped[Optional[List[BaseChunk]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc),
    )
