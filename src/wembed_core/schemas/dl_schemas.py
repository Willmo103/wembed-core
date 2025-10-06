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
        from_attributes = True
