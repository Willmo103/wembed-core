"""
source: wembed_core:models.indexed_image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for file records in the 'host_files' table.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class IndexedImage(AppBase):
    """
    SQLAlchemy model for an image file.

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
        b64_string (str, optional): Base64 encoded string of the image content.
        exif_raw (bytes, optional): Raw EXIF metadata.
        exif_json (str, optional): EXIF metadata in JSON format.
    """

    __tablename__ = "indexed_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    suffix: Mapped[str] = mapped_column(String, nullable=False)
    sha256: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    md5: Mapped[str] = mapped_column(String, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    mimetype: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    b64_string: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    exif_raw: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    exif_json: Mapped[Optional[str]] = mapped_column(JSON, nullable=True)
    ctime_iso: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    mtime_iso: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
    )
    host: Mapped[str] = mapped_column(String, nullable=False)
    user: Mapped[str] = mapped_column(String, nullable=False)
    path: Mapped[str] = mapped_column(String, nullable=False)
    relative_path: Mapped[str] = mapped_column(String, nullable=False)
    full_path: Mapped[str] = mapped_column(String, nullable=False)
