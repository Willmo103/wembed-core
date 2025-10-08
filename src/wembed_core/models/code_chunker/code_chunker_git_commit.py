"""
wembed_core.models.code_chunker_git_commit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for Git commits.
"""

from datetime import datetime, timezone
from typing import List

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class CodeChunkerGitCommits(AppBase):
    """
    SQLAlchemy model for Git commits.

    Attributes:
        id (int): Unique identifier for the commit record.
        hash (str): The Git commit hash (SHA).
        author (str): The author of the commit.
        date (datetime): The timestamp of the commit.
        message (str): The commit message.
        files_changed (List[str]): A JSON list of files changed in the commit.
        insertions (int): The number of lines inserted.
        deletions (int): The number of lines deleted.
        created_at (datetime): Timestamp when the record was created.
    """

    __tablename__ = "code_chunker_git_commits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hash: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    files_changed: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    insertions: Mapped[int] = mapped_column(Integer, nullable=False)
    deletions: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
