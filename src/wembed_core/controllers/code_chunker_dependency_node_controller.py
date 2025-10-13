"""
wembed_core/controllers/code_chunker_dependency_node_controller.py
"""

from typing import List

from wembed_core.database import DatabaseService
from wembed_core.models import CodeChunkerDependencyNodes
from wembed_core.schemas import DependencyNode


class CodeChunkerDependencyNodeController:
    """Controller for CRUD operations on CodeChunkerDependencyNodes."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create_batch(
        self, nodes: List[DependencyNode]
    ) -> List[CodeChunkerDependencyNodes]:
        """Creates a batch of dependency node records."""
        with self.db_service.get_db() as session:
            db_records = [CodeChunkerDependencyNodes(**n.model_dump()) for n in nodes]
            session.add_all(db_records)
            session.commit()
            for record in db_records:
                session.refresh(record)
            return db_records
