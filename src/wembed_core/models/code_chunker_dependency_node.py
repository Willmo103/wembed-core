"""
wembed_core.models.code_chunker_dependency_node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for dependency graph nodes.
"""

from datetime import datetime, timezone
from typing import Optional, Set

from sqlalchemy import JSON, Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import AppBase


class CodeChunkerDependencyNodes(AppBase):
    """
    SQLAlchemy model for dependency nodes.

    Attributes:
        id (int): Unique identifier for the record.
        name (str): The name of the dependency (e.g., package name).
        version (Optional[str]): The version of the dependency.
        source (str): The source type ('stdlib', 'local', 'external').
        file_path (Optional[str]): The file path for 'local' dependencies.
        used_by (Set[str]): A JSON set of file paths that use this dependency.
        imports (Set[str]): A JSON set of modules this dependency imports.
        is_used (bool): Flag indicating if the dependency is used.
        created_at (datetime): Timestamp when the record was created.
    """

    __tablename__ = "code_chunker_dependency_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    version: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    file_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    used_by: Mapped[Set[str]] = mapped_column(JSON, nullable=False)
    imports: Mapped[Set[str]] = mapped_column(JSON, nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
