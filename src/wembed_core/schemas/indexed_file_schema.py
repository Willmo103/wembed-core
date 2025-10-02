"""
wembed_core.schemas.file_schemas
Schemas for file records using Pydantic.
"""

from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class IndexedFileSchema(BaseModel):
    id: str = Field(..., description="Unique identifier for the file")
    version: int = Field(1, description="Version number of the file record")
    source_type: str = Field(
        ...,
        max_length=50,
        description="Type of the source (e.g., 'repo', 'vault', 'documentation')",
    )
    source_root: str = Field(..., description="Root path of the source")
    source_name: str = Field(
        ..., description="Name of the source (e.g., repository name)"
    )
    host: Optional[str] = Field(None, description="Hostname where the file is located")
    user: Optional[str] = Field(None, description="User associated with the file")
    name: Optional[str] = Field(None, description="Name of the file")
    stem: Optional[str] = Field(
        None, description="Stem of the file name (name without suffix)"
    )
    path: Optional[str] = Field(None, description="Full path to the file")
    relative_path: Optional[str] = Field(
        None, description="Path relative to the source root"
    )
    suffix: Optional[str] = Field(None, description="File extension/suffix")
    sha256: Optional[str] = Field(
        None, description="SHA-256 hash of the file content (unique)"
    )
    md5: Optional[str] = Field(None, description="MD5 hash of the file content")
    mode: Optional[int] = Field(None, description="File mode/permissions")
    size: Optional[int] = Field(None, description="Size of the file in bytes")
    content: Optional[bytes] = Field(None, description="Binary content of the file")
    content_text: Optional[str] = Field(None, description="Text content of the file")
    ctime_iso: Optional[datetime] = Field(
        None, description="Creation time of the file (ISO format)"
    )
    mtime_iso: Optional[datetime] = Field(
        None, description="Last modified time of the file (ISO format)"
    )
    line_count: Optional[int] = Field(None, description="Number of lines in the file")
    uri: Optional[str] = Field(None, description="URI of the file on the host system")
    mimetype: Optional[str] = Field(None, description="MIME type of the file")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of when the record was created",
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp of when the record was last updated",
    )

    def bump_version(self) -> None:
        """Increment the version number of the file record, indicating an update."""
        self.version += 1
        self.updated_at = datetime.now(timezone.utc)

    class Config:
        """Pydantic configuration to allow ORM mode."""

        from_attributes = True
