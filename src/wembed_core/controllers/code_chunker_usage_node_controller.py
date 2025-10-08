"""
wembed_core/controllers/code_chunker_usage_node_controller.py
"""

from typing import List

from wembed_core.database import DatabaseService
from wembed_core.models import CodeChunkerUsageNodes
from wembed_core.schemas import UsageNode


class CodeChunkerUsageNodeController:
    """Controller for CRUD operations on CodeChunkerUsageNodes."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create_batch(
        self, nodes: List[UsageNode]
    ) -> List[CodeChunkerUsageNodes]:
        """Creates a batch of usage node records."""
        with self.db_service.get_db() as session:
            db_records = [
                CodeChunkerUsageNodes(**n.model_dump()) for n in nodes
            ]
            session.add_all(db_records)
            session.commit()
            for record in db_records:
                session.refresh(record)
            return db_records
