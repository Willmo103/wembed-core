"""
source: wembed_core/models/indexed_files.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from wembed_core.database import AppBase


class IndexedFiles(AppBase):
    """
    SQLAlchemy model for the 'indexed_files' table, representing file records.

    Attributes:
        id (str): Unique identifier for the file (primary key).
        version (int): Version number of the file record.
        source_type (str): Type of the source (e.g., 'git', 'local').
        source_root (str): Root path of the source.
        source_name (str): Name of the source (e.g., repository name).
        host (str): Hostname where the file is located.
        user (str): User associated with the file.
        name (str): Name of the file.
        stem (str): Stem of the file name (name without suffix).
        path (str): Full path to the file.
        relative_path (str): Path relative to the source root.
        suffix (str): File extension/suffix.
        sha256 (str): SHA-256 hash of the file content (unique).
        md5 (str): MD5 hash of the file content.
        mode (int): File mode/permissions.
        size (int): Size of the file in bytes.
        content (bytes, optional): Binary content of the file.
        content_text (str): Text content of the file.
        ctime_iso (datetime): Creation time of the file in ISO format.
        mtime_iso (datetime): Last modification time of the file in ISO format.
        line_count (int): Number of lines in the file.
        uri (str): URI of the file.
        mimetype (str): MIME type of the file.
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
    """

    __tablename__ = "indexed_files"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    source_type: Mapped[str] = mapped_column(String, nullable=False)
    source_root: Mapped[str] = mapped_column(String, nullable=False)
    source_name: Mapped[str] = mapped_column(String, nullable=False)
    host: Mapped[str] = mapped_column(String, nullable=False)
    user: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    stem: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    relative_path: Mapped[str] = mapped_column(String, nullable=False)
    suffix: Mapped[str] = mapped_column(String, nullable=False)
    sha256: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    md5: Mapped[str] = mapped_column(String, nullable=False)
    mode: Mapped[int] = mapped_column(Integer, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    ctime_iso: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    mtime_iso: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    line_count: Mapped[int] = mapped_column(Integer, nullable=False)
    uri: Mapped[str] = mapped_column(String, nullable=False)
    mimetype: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default="now()", onupdate="now()"
    )
