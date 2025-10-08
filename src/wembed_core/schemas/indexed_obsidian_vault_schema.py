from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


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
