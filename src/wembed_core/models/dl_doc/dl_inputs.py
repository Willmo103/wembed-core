from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class DLInputs(AppBase):
    """
    SQLAlchemy model for input records.
    Attributes:
      id (int): Unique identifier for the input record.
      source_ref (str): Unique reference or identifier for the input source.
      source_type (str): Type of the input source (e.g., 'file', 'url').
      status (str): Current status of the input (e.g., 'pending', 'processed', 'error').
      errors (Optional[str]): Any error messages associated with the input.
      added_at (datetime): Timestamp when the input was added.
      processed_at (Optional[datetime]): Timestamp when the input was processed.
      output_doc_id (Optional[int]): Foreign key linking to the output document record.
    """

    __tablename__ = "dl_inputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    source_ref: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True
    )
    status: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    errors: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    output_doc_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("dl_documents.id"), nullable=True, index=True
    )
