"""
Pydantic schemas for Document and Chunk models.
"""

from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class DLChunkSchema(BaseModel):
    id: Optional[int] = None
    document_id: int
    idx: int
    text_chunk: str
    embedding: List[float]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        """
        Pydantic configuration to allow population from ORM objects.
        """

        from_attributes = True


class DLDocumentSchema(BaseModel):
    id: Optional[int] = None
    source: str
    source_type: str
    source_ref: str
    dl_doc: Optional[str] = None
    markdown: str
    html: str
    text: str
    doctags: Optional[str] = None
    chunks_json: Optional[List[DLChunkSchema]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None

    class Config:
        """
        Pydantic configuration to allow population from ORM objects.
        """

        from_attributes = True


class DLInputSchema(BaseModel):
    id: Optional[int] = None
    source: str
    source_ref: str
    source_type: str
    status: int = Field(
        ..., description="Status code representing the input processing state"
    )
    errors: Optional[List[str]] = Field(
        lambda: [], description="List of error messages, if any"
    )
    added_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    processed_at: Optional[datetime] = None
    output_doc_id: Optional[int] = None

    class Config:
        """
        Pydantic configuration to allow population from ORM objects.
        """

        from_attributes = True
