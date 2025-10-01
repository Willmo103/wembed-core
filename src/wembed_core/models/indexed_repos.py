from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from ..database import AppBase


class IndexedRepos(AppBase):
    """
    Represents a code repository in the database.

    Attributes:
        id (int): Primary key.
        repo_name (str): Name of the repository.
        host (str): Host of the repository (e.g., GitHub, GitLab).
        root_path (str): Root path of the repository.
        files (List[str], optional): List of file paths in the repository.
        file_count (int): Number of files in the repository.
        indexed_at (datetime, optional): Timestamp of the last indexing operation.
    """

    __tablename__ = "indexed_repos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    repo_name: Mapped[str] = mapped_column(String, nullable=False)
    host: Mapped[str] = mapped_column(String, nullable=False)
    root_path: Mapped[str] = mapped_column(String, nullable=False)
    files: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    file_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    indexed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
