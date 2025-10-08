"""
wembed_core/controllers/indexed_file_controller.py
"""

from typing import List, Optional

from wembed_core.database import DatabaseService
from wembed_core.models.indexing.indexed_files import IndexedFiles
from wembed_core.schemas.indexed_file_schema import IndexedFileSchema


class IndexedFileController:
    """Controller for CRUD operations on IndexedFiles."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create(self, file_data: IndexedFileSchema) -> IndexedFiles:
        """Creates a new file record."""
        with self.db_service.get_db() as session:
            db_record = IndexedFiles(**file_data.model_dump())
            session.add(db_record)
            session.commit()
            session.refresh(db_record)
        return db_record

    def get_by_id(self, file_id: str) -> Optional[IndexedFiles]:
        """Retrieves a file record by its ID."""
        with self.db_service.get_db() as session:
            res = session.query(IndexedFiles).filter(IndexedFiles.id == file_id).first()
        return res

    def get_by_sha256(self, sha256: str) -> Optional[IndexedFiles]:
        """Retrieves a file record by its SHA256 hash."""
        with self.db_service.get_db() as session:
            res = (
                session.query(IndexedFiles)
                .filter(IndexedFiles.sha256 == sha256)
                .first()
            )
        return res

    def get_by_source_name(self, source_name: str) -> List[IndexedFiles]:
        """Retrieves file records by the source name (e.g., repo name)."""
        with self.db_service.get_db() as session:
            res = (
                session.query(IndexedFiles)
                .filter(IndexedFiles.source_name == source_name)
                .all()
            )
        return res

    def update(
        self, file_id: str, file_data: IndexedFileSchema
    ) -> Optional[IndexedFiles]:
        """Updates an existing file record."""
        with self.db_service.get_db() as session:
            db_record = self.get_by_id(file_id)
            if db_record:
                update_data = file_data.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(db_record, key, value)
                session.commit()
                session.refresh(db_record)
        return db_record

    def delete(self, file_id: str) -> bool:
        """Deletes a file record by its ID."""
        with self.db_service.get_db() as session:
            db_record = self.get_by_id(file_id)
        if db_record:
            with self.db_service.get_db() as session:
                session.delete(db_record)
                session.commit()
            return True
        return False
