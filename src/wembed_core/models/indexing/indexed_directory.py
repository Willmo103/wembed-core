"""
 wembed_core/models/indexing/directory.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 SQLAlchemy model for code directories."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class IndexedDirectory(AppBase):
    """
    Represents a code directory in the database.

    Attributes:
        id (int) NOT NULL: Primary key.
        dir_type (str) NOT NULL: Name of the repository.
        host (str): Host where the repository was indexed
        root_path (str): Root path of the repository.
        files (List[str], optional): List of file paths in the repository.
        file_count (int): Number of files in the repository.
        indexed_at (datetime, optional): Timestamp of the last indexing operation.
    """

    __tablename__ = "indexed_repos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dir_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    host: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    root_path: Mapped[str] = mapped_column(String, nullable=False)
    files: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True, default=[])
    file_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    indexed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
