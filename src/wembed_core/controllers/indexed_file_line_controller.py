"""
wembed_core/controllers/indexed_file_line_controller.py
"""

from typing import List, Optional

from wembed_core.database import DatabaseService
from wembed_core.models.indexed_file_lines import IndexedFileLines
from wembed_core.schemas.indexed_file_line_schema import IndexedFileLineSchema


class IndexedFileLineController:
    """Controller for CRUD operations on IndexedFileLines."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create(self, line_data: IndexedFileLineSchema) -> IndexedFileLines:
        """Creates a new file line record."""
        with self.db_service.get_db() as session:
            db_record = IndexedFileLines(**line_data.model_dump())
            session.add(db_record)
            session.commit()
            session.refresh(db_record)
            return db_record

    def create_batch(
        self, lines: List[IndexedFileLineSchema]
    ) -> List[IndexedFileLines]:
        """Creates multiple file line records in a single batch."""
        with self.db_service.get_db() as session:
            db_records = [IndexedFileLines(**line.model_dump()) for line in lines]
            session.add_all(db_records)
            session.commit()
            for record in db_records:
                session.refresh(record)
            return db_records

    def get_by_file_id(self, file_id: str) -> List[IndexedFileLines]:
        """Retrieves all lines for a given file ID."""
        with self.db_service.get_db() as session:
            return (
                session.query(IndexedFileLines)
                .filter(IndexedFileLines.file_id == file_id)
                .order_by(IndexedFileLines.line_number)
                .all()
            )

    def get_lines_without_embeddings(self, file_id: str) -> List[IndexedFileLines]:
        """Retrieves all lines for a file that do not yet have an embedding."""
        with self.db_service.get_db() as session:
            return (
                session.query(IndexedFileLines)
                .filter(
                    IndexedFileLines.file_id == file_id,
                    IndexedFileLines.embedding.is_(None),
                )
                .all()
            )

    def update_embedding(
        self, line_id: int, embedding: List[float]
    ) -> Optional[IndexedFileLines]:
        """Updates the embedding for a specific line by its primary key."""
        with self.db_service.get_db() as session:
            db_record = (
                session.query(IndexedFileLines)
                .filter(IndexedFileLines.id == line_id)
                .first()
            )
            if db_record:
                db_record.embedding = embedding
                session.commit()
                session.refresh(db_record)
            return db_record

    def delete_by_file_id(self, file_id: str) -> int:
        """Deletes all lines associated with a file ID."""
        with self.db_service.get_db() as session:
            deleted_count = (
                session.query(IndexedFileLines)
                .filter(IndexedFileLines.file_id == file_id)
                .delete()
            )
            session.commit()
            return deleted_count
