"""
wembed_core/controllers/code_chunker_git_branch_controller.py
"""

from typing import List

from wembed_core.database import DatabaseService
from wembed_core.models import CodeChunkerGitBranches
from wembed_core.schemas import GitBranchSchema


class CodeChunkerGitBranchController:
    """Controller for CRUD operations on CodeChunkerGitBranches."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create_batch(
        self, branches: List[GitBranchSchema]
    ) -> List[CodeChunkerGitBranches]:
        """Creates or updates a batch of branch records."""
        with self.db_service.get_db() as session:
            db_records = [CodeChunkerGitBranches(**b.model_dump()) for b in branches]
            session.add_all(db_records)
            session.commit()
            for record in db_records:
                session.refresh(record)
            return db_records

    def get_all(self) -> List[CodeChunkerGitBranches]:
        """Retrieves all branch records."""
        with self.db_service.get_db() as session:
            return session.query(CodeChunkerGitBranches).all()

    def delete_all(self) -> int:
        """Deletes all branch records."""
        with self.db_service.get_db() as session:
            deleted_count = session.query(CodeChunkerGitBranches).delete()
            session.commit()
            return deleted_count
