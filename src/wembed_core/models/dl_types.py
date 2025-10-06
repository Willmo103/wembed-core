"""
wembed_core.models.dl_types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Database models for input sources and document types.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import AppBase


class DLInputSources(AppBase):
    """
    SQLAlchemy model for input sources.
    Attributes:
      id (int): Unique identifier for the input source record.
      source_name (str): Name of the input source (e.g., 'file', 'url').
      description (Optional[str]): Description of the input source.
      added_at (datetime): Timestamp when the input source was added.
      frozen (bool): Flag indicating if the input source is frozen (immutable).
    """

    __tablename__ = "dl_input_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    frozen: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
