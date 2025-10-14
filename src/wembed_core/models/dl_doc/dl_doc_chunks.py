"""
 wembed_core/models/dl_doc/dl_doc_chunks.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 SQLAlchemy model for document chunks.
"""

from datetime import datetime, timezone
from typing import List

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class DLChunks(AppBase):
    """
    SQLAlchemy model for document chunks.
    Attributes:
      id (int): Unique identifier for the chunk.
      document_id (int): Foreign key referencing the associated document.
      chunk_index (int): Index of the chunk within the document.
      text_chunk (str): The text content of the chunk.
      embedding (List[float]): The embedding vector for the chunk.
      created_at (datetime): Timestamp when the chunk was created.
    """

    __tablename__ = "dl_doc_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        ForeignKey("dl_doc.id"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    embedding: Mapped[List[float]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
