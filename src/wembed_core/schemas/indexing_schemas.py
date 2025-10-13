"""
wembed_core/schemas/indexing_schemas.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Schemas for indexing results, repositories, Obsidian vaults, files, and file lines.
"""

from datetime import datetime, timezone
from typing import Generator, List, Optional

from pydantic import BaseModel, Field, computed_field


class IndexingResultSchema(BaseModel):
    id: str
    root_path: str
    scan_name: str
    scan_type: str
    files: Optional[List[str]] = None
    scan_start: datetime = datetime.now(tz=timezone.utc)
    scan_end: Optional[datetime] = None
    duration: Optional[float] = None
    options: Optional[dict] = None
    user: str
    host: str

    @computed_field
    def total_files(self) -> int:
        """Compute the total number of files in the scan result."""
        return len(self.files) if self.files else 0

    class Config:
        """Pydantic configuration to allow ORM mode."""

        exclude = {"total_files"}
        from_attributes = True


class IndexingResultsListSchema(BaseModel):
    results: List[IndexingResultSchema]

    def add_result(self, result: IndexingResultSchema) -> None:
        """
        Add a scan result to the list.
        Args:
            result (IndexingResultSchema): The scan result to add.

        Returns:
            None
        """
        self.results.append(result)

    def iter_results(self) -> Generator[IndexingResultSchema, None, None]:
        """
        Generator to iterate over scan results.

        Returns:
            Generator[IndexingResultSchema, None, None]: A generator of scan results.
        """
        for result in self.results:
            yield result


class IndexedRepoSchema(BaseModel):
    id: Optional[int] = None
    repo_name: str
    host: str
    root_path: str
    files: Optional[List[str]] = None
    file_count: int = 0
    indexed_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration for ORM compatibility."""

        from_attributes = True
        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat() if v else None}


class IndexedObsidianVaultSchema(BaseModel):
    id: Optional[int] = None
    vault_name: str
    host: str
    root_path: str
    files: Optional[List[str]] = None
    file_count: int = 0
    indexed_at: Optional[datetime] = None

    class Config:
        """Pydantic configuration for ORM compatibility."""

        from_attributes = True


class IndexedFileLineSchema(BaseModel):
    """Pydantic schema for an indexed file line."""

    id: Optional[int] = Field(None, description="Unique identifier for the file line")
    file_id: str = Field(..., description="Foreign key to the associated file record")
    file_source_name: str = Field(
        ..., description="Name of the source (e.g., repo name)"
    )
    file_source_type: str = Field(..., description="Type of the source (e.g., 'git')")
    line_number: int = Field(..., description="Line number in the file")
    line_text: str = Field(..., description="Text content of the line")
    embedding: Optional[List[float]] = Field(
        None, description="Embedding vector for the line"
    )
    created_at: Optional[datetime] = Field(None, description="Timestamp of creation")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


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


__all__ = [
    "IndexingResultSchema",
    "IndexingResultsListSchema",
    "IndexedRepoSchema",
    "IndexedObsidianVaultSchema",
    "IndexedFileLineSchema",
    "IndexedFileSchema",
]
