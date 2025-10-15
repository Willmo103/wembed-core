"""
wembed_core/models/dl_doc/dl_inputs.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for input records.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class DLInputs(AppBase):
    """
    SQLAlchemy model for input records.
    Attributes:
      id (int): Unique identifier for the input record.
      source (str): The path or URL of the input source.
      channel (str): Name of the processing channel.
      html_input (Optional[str]): The raw HTML input content.
      errors (Optional[str]): Any error messages associated with the input.
      added_at (datetime): Timestamp when the input was added.
      processed_at (Optional[datetime]): Timestamp when the input was processed.
      output_doc_id (Optional[int]): Foreign key linking to the output document record.
      meta (Optional[dict]): Additional metadata associated with the input.
    """

    __tablename__ = "dl_inputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(2048), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    html_input: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    errors: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    output_doc_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("dl_doc.id"), nullable=True, index=True
    )
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
