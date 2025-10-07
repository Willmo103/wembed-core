"""
wembed_core.models.code_chunker_git_branch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for Git branches.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import AppBase


class CodeChunkerGitBranches(AppBase):
    """
    SQLAlchemy model for Git branch metadata.

    Attributes:
        id (int): Unique identifier for the record.
        name (str): The name of the branch.
        last_commit (str): The hash of the last commit on this branch.
        last_commit_date (datetime): The timestamp of the last commit.
        is_current (bool): True if this is the currently checked-out branch.
        created_at (datetime): Timestamp when the record was created.
        updated_at (Optional[datetime]): Timestamp when the record was last updated.
    """

    __tablename__ = "code_chunker_git_branches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    last_commit: Mapped[str] = mapped_column(String(40), nullable=False)
    last_commit_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)
    )
