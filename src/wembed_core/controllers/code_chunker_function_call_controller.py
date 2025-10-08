"""
wembed_core/controllers/code_chunker_function_call_controller.py
"""

from typing import List

from wembed_core.database import DatabaseService
from wembed_core.models import CodeChunkerFunctionCalls
from wembed_core.schemas import FunctionCall


class CodeChunkerFunctionCallController:
    """Controller for CRUD operations on CodeChunkerFunctionCalls."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create_batch(
        self, calls: List[FunctionCall]
    ) -> List[CodeChunkerFunctionCalls]:
        """Creates a batch of function call records."""
        with self.db_service.get_db() as session:
            db_records = [
                CodeChunkerFunctionCalls(**c.model_dump()) for c in calls
            ]
            session.add_all(db_records)
            session.commit()
            for record in db_records:
                session.refresh(record)
            return db_records
