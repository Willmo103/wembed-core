"""
wembed_core.models.code_chunker_import_statement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for import statements.
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import JSON, Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class CodeChunkerImportStatements(AppBase):
    """
    SQLAlchemy model for parsed import statements.

    Attributes:
        id (int): Unique identifier for the record.
        module (str): The module being imported (e.g., 'os' or 'os.path').
        names (List[str]): Specific names imported from the module.
        alias (Optional[str]): The alias for the import (e.g., 'np' for 'numpy').
        file_path (str): The file where the import statement is located.
        line_number (int): The line number of the import statement.
        is_from_import (bool): True for 'from x import y', False for 'import x'.
        created_at (datetime): Timestamp when the record was created.
    """

    __tablename__ = "code_chunker_import_statements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    module: Mapped[str] = mapped_column(String, nullable=False)
    names: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    alias: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False, index=True)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_from_import: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
