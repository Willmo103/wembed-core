"""
wembed_core/controllers/scan_result_controller.py
"""

from typing import List, Optional

from wembed_core.database import DatabaseService
from wembed_core.models.indexing_results import FileIndexingResults
from wembed_core.schemas.indexing_result_schemas import IndexingResultSchema


class IndexingResultsController:
    """Controller for CRUD operations on FileIndexingResults."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create(self, scan_data: IndexingResultSchema) -> FileIndexingResults:
        """Creates a new scan result record."""
        with self.db_service.get_db() as session:
            dump = scan_data.model_dump()
            db_record = FileIndexingResults(**dump)
            session.add(db_record)
            session.commit()
            session.refresh(db_record)
            return db_record

    def get_by_id(self, scan_id: str) -> Optional[FileIndexingResults]:
        """Retrieves a scan result by its ID."""
        with self.db_service.get_db() as session:
            return (
                session.query(FileIndexingResults)
                .filter(FileIndexingResults.id == scan_id)
                .first()
            )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[FileIndexingResults]:
        """Retrieves all scan results with pagination."""
        with self.db_service.get_db() as session:
            return session.query(FileIndexingResults).offset(skip).limit(limit).all()

    def delete(self, scan_id: str) -> bool:
        """Deletes a scan result by its ID."""
        with self.db_service.get_db() as session:
            db_record = self.get_by_id(scan_id)
            if db_record:
                session.delete(db_record)
                session.commit()
                return True
            return False
