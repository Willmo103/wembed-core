"""
wembed_core/controllers/code_chunker_import_statement_controller.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Controller for CRUD operations on CodeChunkerImportStatements.
"""

from typing import List

from wembed_core.database import DatabaseService
from wembed_core.models import CodeChunkerImportStatements
from wembed_core.schemas import ImportStatement


class CodeChunkerImportStatementController:
    """Controller for CRUD operations on CodeChunkerImportStatements."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create_batch(
        self, imports: List[ImportStatement]
    ) -> List[CodeChunkerImportStatements]:
        """Creates a batch of import statement records."""
        with self.db_service.get_db() as session:
            db_records = [
                CodeChunkerImportStatements(**i.model_dump()) for i in imports
            ]
            session.add_all(db_records)
            session.commit()
            for record in db_records:
                session.refresh(record)
            return db_records
