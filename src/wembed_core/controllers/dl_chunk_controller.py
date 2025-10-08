"""
wembed_core/controllers/dl_chunk_controller.py
"""

from typing import List, Optional

from wembed_core.database import DatabaseService
from wembed_core.models.dl_chunks import DLChunks
from wembed_core.schemas.dl_schemas import DLChunkSchema


class DLChunkController:
    """Controller for CRUD operations on DLChunks."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create(self, chunk: DLChunkSchema) -> DLChunks:
        """Creates a new chunk record."""
        with self.db_service.get_db() as session:
            db_record = DLChunks(**chunk.model_dump())
            session.add(db_record)
            session.commit()
            session.refresh(db_record)
        return db_record

    def create_batch(self, chunks: List[DLChunkSchema]) -> List[DLChunks]:
        """Creates multiple chunk records in a single batch."""
        with self.db_service.get_db() as session:
            db_records = [DLChunks(**chunk.model_dump()) for chunk in chunks]
            session.add_all(db_records)
            session.commit()
            for record in db_records:
                session.refresh(record)
        return db_records

    def get_by_id(self, chunk_id: int) -> Optional[DLChunks]:
        """Retrieves a chunk by its ID."""
        with self.db_service.get_db() as session:
            res = (
                session.query(DLChunks).filter(DLChunks.id == chunk_id).first()
            )
        return res

    def get_by_document_id(self, document_id: int) -> List[DLChunks]:
        """Retrieves all chunks for a given document ID."""
        with self.db_service.get_db() as session:
            res = (
                session.query(DLChunks)
                .filter(DLChunks.document_id == document_id)
                .order_by(DLChunks.chunk_index)
                .all()
            )
        return res

    def delete_by_document_id(self, document_id: int) -> int:
        """Deletes all chunks associated with a document ID."""
        with self.db_service.get_db() as session:
            db_record = self.get_by_id(document_id)
        if db_record:
            with self.db_service.get_db() as session:
                session.delete(db_record)
                session.commit()
            return True
        return False
