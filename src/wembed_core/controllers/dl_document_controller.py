"""
wembed_core/controllers/dl_document_controller.py
"""

from datetime import datetime, timezone
from typing import List, Optional

from wembed_core.database import DatabaseService
from wembed_core.models.dl_doc.dl_documents import DLDocuments
from wembed_core.schemas.dl_doc_schemas import DLDocumentSchema


class DLDocumentController:
    """Controller for CRUD operations on DLDocuments."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create(self, document: DLDocumentSchema) -> DLDocuments:
        """Creates a new document record."""
        with self.db_service.get_db() as session:
            db_record = DLDocuments(**document.model_dump())
            session.add(db_record)
            session.commit()
            session.refresh(db_record)
        return db_record

    def get_by_id(self, doc_id: int) -> Optional[DLDocuments]:
        """Retrieves a document by its ID."""
        with self.db_service.get_db() as session:
            res = session.query(DLDocuments).filter(DLDocuments.id == doc_id).first()
        return res

    def get_by_source(self, source: str) -> Optional[DLDocuments]:
        """Retrieves a document by its source path/URL."""
        with self.db_service.get_db() as session:
            res = (
                session.query(DLDocuments).filter(DLDocuments.source == source).first()
            )
        return res

    def get_all(self, skip: int = 0, limit: int = 100) -> List[DLDocuments]:
        """Retrieves all documents with pagination."""
        with self.db_service.get_db() as session:
            res = session.query(DLDocuments).offset(skip).limit(limit).all()
        return res

    def update(self, doc_id: int, document: DLDocumentSchema) -> Optional[DLDocuments]:
        """Updates an existing document."""
        with self.db_service.get_db() as session:
            db_record = (
                session.query(DLDocuments).filter(DLDocuments.id == doc_id).first()
            )
            if db_record:
                update_data = document.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(db_record, key, value)
                db_record.updated_at = datetime.now(timezone.utc)
                session.commit()
                session.refresh(db_record)
        return db_record

    def delete(self, doc_id: int) -> bool:
        """Deletes a document by its ID."""
        with self.db_service.get_db() as session:
            db_record = self.get_by_id(doc_id)
        if db_record:
            with self.db_service.get_db() as session:
                session.delete(db_record)
                session.commit()
            return True
        return False
