"""
wembed_core/schemas/indexed_file_line_schema.py
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class IndexedFileLineSchema(BaseModel):
    """Pydantic schema for an indexed file line."""

    id: Optional[int] = Field(
        None, description="Unique identifier for the file line"
    )
    file_id: str = Field(
        ..., description="Foreign key to the associated file record"
    )
    file_source_name: str = Field(
        ..., description="Name of the source (e.g., repo name)"
    )
    file_source_type: str = Field(
        ..., description="Type of the source (e.g., 'git')"
    )
    line_number: int = Field(..., description="Line number in the file")
    line_text: str = Field(..., description="Text content of the line")
    embedding: Optional[List[float]] = Field(
        None, description="Embedding vector for the line"
    )
    created_at: Optional[datetime] = Field(
        None, description="Timestamp of creation"
    )

    class Config:
        """Pydantic configuration."""

        from_attributes = True
