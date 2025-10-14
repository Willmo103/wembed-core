"""
source: wembed_core/models/indexing_results.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for file records in the 'host_files' table.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class FileIndexingResults(AppBase):
    """
    SQLAlchemy model for scan results.

    Attributes:
      id (str): Unique identifier for the scan result.
      root_path (str): The root path that was scanned.
      scan_mode (str): The mode of the scan (e.g., 'automatic', 'manual').
      found_files (Optional[List[str]]): List of file paths found during the scan.
      scan_start (datetime): Timestamp when the scan started.
      scan_end (Optional[datetime]): Timestamp when the scan ended.
      duration (Optional[int]): Duration of the scan in seconds.
    """

    __tablename__ = "indexing_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True, index=True)
    root_path: Mapped[str] = mapped_column(String, nullable=False, index=True)
    scan_mode: Mapped[str] = mapped_column(String, nullable=False, index=True)
    found_files: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    scan_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    scan_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.found_files is not None:
            self.total_files = len(self.found_files)
        else:
            self.total_files = 0
