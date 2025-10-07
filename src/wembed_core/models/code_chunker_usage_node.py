"""
wembed_core.models.code_chunker_usage_node
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for usage graph nodes.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import AppBase


class CodeChunkerUsageNodes(AppBase):
    """
    SQLAlchemy model for usage graph nodes.

    Attributes:
        id (int): Unique identifier for the record.
        identifier (str): The name of the function, class, method, etc.
        file_path (str): The file where the identifier is defined.
        node_type (str): The type of node ('function', 'class', 'method').
        start_line (int): The starting line number of the definition.
        end_line (int): The ending line number of the definition.
        is_entry_point (bool): True if this node is a potential entry point.
        complexity_score (int): A calculated complexity score (e.g., cyclomatic).
        created_at (datetime): Timestamp when the record was created.
    """

    __tablename__ = "code_chunker_usage_nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    identifier: Mapped[str] = mapped_column(String, nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    is_entry_point: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    complexity_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
