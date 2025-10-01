"""
source: wembed_core/models/scan_result.py
SQLAlchemy model for file records in the 'host_files' table.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    DateTime,
    Integer,
    LargeBinary,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from ..database import AppBase as Base


class ScanResultRecord(Base):
    """
    SQLAlchemy model for scan results.

    Attributes:
    - id (str): Unique identifier for the scan result.
    - root_path (str): The root path that was scanned.
    - scan_type (str): The type of scan performed (e.g., 'full', 'incremental').
    - scan_name (Optional[str]): An optional name for the scan.
    - files (Optional[List[str]]): List of file paths found during the scan.
    - scan_start (datetime): Timestamp when the scan started.
    - scan_end (Optional[datetime]): Timestamp when the scan ended.
    - duration (Optional[int]): Duration of the scan in seconds.
    - options (Optional[dict]): Additional options used during the scan.
    - user (str): The user who initiated the scan.
    - host (str): The host where the scan was performed.
    """

    __tablename__ = "scan_results"

    id: Mapped[str] = mapped_column(String, primary_key=True, unique=True, index=True)
    root_path: Mapped[str] = mapped_column(String, nullable=False, index=True)
    scan_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    scan_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    files: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    scan_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    scan_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    options: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    user: Mapped[str] = mapped_column(String, nullable=False)
    host: Mapped[str] = mapped_column(String, nullable=False)