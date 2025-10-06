"""
SQLAlchemy model for indexed file lines with embeddings.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class IndexedFileLines(AppBase):
    """
    SQLAlchemy model for a line in a file, including its embedding.

    Attributes:
        id (int): Primary key.
        file_id (str): Foreign key to the associated file.
        file_source_name (str): Name of the repository the file belongs to.
        file_source_type (str): Type of the repository (e.g., git, svn).
        line_number (int): Line number in the file.
        line_text (str): Text content of the line.
        embedding (Optional[List[float]]): Embedding vector for the line.
        created_at (datetime): Timestamp of when the record was created.
    """

    __tablename__ = "indexed_file_lines"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_id: Mapped[str] = mapped_column(
        ForeignKey("indexed_files.id"), nullable=False, index=True
    )
    file_source_name: Mapped[str] = mapped_column(String, nullable=False)
    file_source_type: Mapped[str] = mapped_column(String, nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    line_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
