"""
source: src/wembed_core/models/indexing/indexed_structured.py
~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for structured data indexing.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class IndexedStructured(AppBase):
    """
    Represents structured data in the database.

    Attributes:
        id (str): Unique identifier for the file (primary key).
        version (int): Version number of the file record.
        host (str): Hostname where the file is located.
        name (str): Name of the file.
        stem (str): Stem of the file name (name without suffix).
        path (str): Full path to the file.
        suffix (str): File extension/suffix.
        sha256 (str): SHA-256 hash of the file content (unique).
        md5 (str): MD5 hash of the file content.
        size (int): Size of the file in bytes.
        content (bytes, optional): Binary content of the file.
        ctime_iso (datetime): Creation time of the file in ISO format.
        mtime_iso (datetime): Last modification time of the file in ISO format.
        uri (str): URI of the file.
        mimetype (str): MIME type of the file.
        created_at (datetime): Timestamp when the record was created.
        updated_at (datetime): Timestamp when the record was last updated.
        index_mapping (str): JSON string representing the index mapping.
        index_settings (str): JSON string representing the index settings.
        exporter_script (str): Script used for exporting the structured data.
    """

    __tablename__ = "indexed_structured"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    host: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    stem: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    suffix: Mapped[str] = mapped_column(String, nullable=False)
    sha256: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    md5: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    ctime_iso: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mtime_iso: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    uri: Mapped[str] = mapped_column(String, nullable=False)
    mimetype: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    index_mapping: Mapped[str] = mapped_column(String, nullable=True)
    index_settings: Mapped[str] = mapped_column(String, nullable=True)
    exporter_script: Mapped[str] = mapped_column(String, nullable=True)
