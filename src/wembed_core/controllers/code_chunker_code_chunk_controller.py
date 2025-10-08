"""
wembed_core/controllers/code_chunker_code_chunk_controller.py
"""

from typing import List, Optional

from wembed_core.database import DatabaseService
from wembed_core.models import CodeChunkerCodeChunks
from wembed_core.schemas import CodeChunk


class CodeChunkerCodeChunksController:
    """Controller for CRUD operations on CodeChunkerCodeChunks."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create(self, chunk_data: CodeChunk) -> CodeChunkerCodeChunks:
        """Creates a new code chunk record."""
        with self.db_service.get_db() as session:
            db_record = CodeChunkerCodeChunks(**chunk_data.model_dump())
            session.add(db_record)
            session.commit()
            session.refresh(db_record)
            return db_record

    def create_batch(self, chunks: List[CodeChunk]) -> List[CodeChunkerCodeChunks]:
        """Creates multiple chunk records in a batch."""
        with self.db_service.get_db() as session:
            db_records = [CodeChunkerCodeChunks(**c.model_dump()) for c in chunks]
            session.add_all(db_records)
            session.commit()
            for record in db_records:
                session.refresh(record)
            return db_records

    def get_by_id(self, chunk_id: int) -> Optional[CodeChunkerCodeChunks]:
        """Retrieves a code chunk by its primary key ID."""
        with self.db_service.get_db() as session:
            return (
                session.query(CodeChunkerCodeChunks)
                .filter(CodeChunkerCodeChunks.id == chunk_id)
                .first()
            )

    def get_by_uuid(self, chunk_uuid: str) -> Optional[CodeChunkerCodeChunks]:
        """Retrieves a code chunk by its unique UUID."""
        with self.db_service.get_db() as session:
            return (
                session.query(CodeChunkerCodeChunks)
                .filter(CodeChunkerCodeChunks.chunk_uuid == chunk_uuid)
                .first()
            )

    def get_by_file_path(self, file_path: str) -> List[CodeChunkerCodeChunks]:
        """Retrieves all chunks for a specific file path."""
        with self.db_service.get_db() as session:
            return (
                session.query(CodeChunkerCodeChunks)
                .filter(CodeChunkerCodeChunks.file_path == file_path)
                .all()
            )
