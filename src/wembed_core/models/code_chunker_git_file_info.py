"""
wembed_core.models.code_chunker_git_file_info
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for Git file information.
"""

from datetime import datetime, timezone
from typing import Optional, Set

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import AppBase


class CodeChunkerGitFileInfo(AppBase):
    """
    SQLAlchemy model for Git file metadata.

    Attributes:
        id (int): Unique identifier for the record.
        file_path (str): The path to the file within the repository.
        last_commit_hash (str): The hash of the last commit that modified the file.
        last_author (str): The author of the last modification.
        last_modified (datetime): The timestamp of the last modification.
        total_commits (int): The total number of commits affecting this file.
        contributors (Set[str]): A JSON set of all contributors to this file.
        lines_added_total (int): Total lines added to the file over its history.
        lines_removed_total (int): Total lines removed from the file.
        creation_date (datetime): The timestamp of the file's creation commit.
        created_at (datetime): Timestamp when the record was created.
        updated_at (Optional[datetime]): Timestamp when the record was last updated.
    """

    __tablename__ = "code_chunker_git_file_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False, index=True)
    last_commit_hash: Mapped[str] = mapped_column(String(40), nullable=False)
    last_author: Mapped[str] = mapped_column(String, nullable=False)
    last_modified: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    total_commits: Mapped[int] = mapped_column(Integer, nullable=False)
    contributors: Mapped[Set[str]] = mapped_column(JSON, nullable=False)
    lines_added_total: Mapped[int] = mapped_column(Integer, nullable=False)
    lines_removed_total: Mapped[int] = mapped_column(Integer, nullable=False)
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)
    )
