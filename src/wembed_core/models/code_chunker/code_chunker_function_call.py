"""
wembed_core.models.code_chunker_function_call
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for function calls.
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class CodeChunkerFunctionCalls(AppBase):
    """
    SQLAlchemy model for representing a function call.

    Attributes:
        id (int): Unique identifier for the record.
        caller_file (str): The file where the function call occurs.
        caller_function (str): The function or method making the call.
        called_function (str): The function being called.
        line_number (int): The line number of the function call.
        context (str): The line of code or context of the call.
        created_at (datetime): Timestamp when the record was created.
    """

    __tablename__ = "code_chunker_function_calls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    caller_file: Mapped[str] = mapped_column(String, nullable=False, index=True)
    caller_function: Mapped[str] = mapped_column(String, nullable=False, index=True)
    called_function: Mapped[str] = mapped_column(String, nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    context: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
