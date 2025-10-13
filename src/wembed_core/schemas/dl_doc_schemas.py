"""
Pydantic schemas for Document and Chunk models.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
These schemas define the structure and validation for deep learning documents and their associated chunks.
"""

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class DLChunkSchema(BaseModel):
    id: Optional[int] = None
    document_id: Optional[int] = None
    chunk_index: Optional[int] = None
    chunk_text: Optional[str] = None
    embedding: Optional[List[float]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        """
        Pydantic configuration to allow population from ORM objects.
        """

        from_attributes = True


class DLDocumentSchema(BaseModel):
    id: Optional[int] = None
    source: Optional[str] = None
    source_type: Optional[str] = None
    source_ref: Optional[str] = None
    dl_doc: Optional[str] = None
    markdown: Optional[str] = None
    html: Optional[str] = None
    text: Optional[str] = None
    doctags: Optional[str] = None
    chunks_json: Optional[List[DLChunkSchema]] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    class Config:
        """
        Pydantic configuration to allow population from ORM objects.
        """

        from_attributes = True


class DLInputSchema(BaseModel):
    id: Optional[int] = None
    source_ref: str
    source_type: str
    status: int = Field(
        ..., description="Status code representing the input processing state"
    )
    errors: Optional[List[str]] = Field(
        [], description="List of error messages, if any"
    )
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None
    output_doc_id: Optional[int] = None

    class Config:
        """
        Pydantic configuration to allow population from ORM objects.
        """

        from_attributes = True


__all__ = ["DLChunkSchema", "DLDocumentSchema", "DLInputSchema"]
