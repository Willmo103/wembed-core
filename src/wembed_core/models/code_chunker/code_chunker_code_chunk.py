"""
wembed_core.models.code_chunker_code_chunk
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for code chunks.
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, Set

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class CodeChunkerCodeChunks(AppBase):
    """
    SQLAlchemy model for parsed code chunks.

    Attributes:
        id (int): Unique identifier for the chunk record.
        chunk_uuid (str): The unique UUID for the code chunk.
        content (str): The actual source code content of the chunk.
        chunk_type (str): The type of chunk (e.g., 'function', 'class').
        file_path (str): The file path where the chunk is located.
        start_line (int): The starting line number of the chunk.
        end_line (int): The ending line number of the chunk.
        parent_id (Optional[str]): The UUID of the parent chunk, if any.
        dependencies (Set[str]): A JSON set of dependencies for this chunk.
        docstring (Optional[str]): The docstring associated with the chunk.
        created_at (datetime): Timestamp when the record was created.
    """

    __tablename__ = "code_chunker_code_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chunk_uuid: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid.uuid4()), unique=True, index=True
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_type: Mapped[str] = mapped_column(String, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False, index=True)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    dependencies: Mapped[Set[str]] = mapped_column(JSON, nullable=True)
    docstring: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
