"""
wembed_core/controllers/code_chunker_git_commit_controller.py
"""

from typing import List, Optional

from wembed_core.database import DatabaseService
from wembed_core.models import CodeChunkerGitCommits
from wembed_core.schemas import GitCommitSchema


class CodeChunkerGitCommitController:
    """Controller for CRUD operations on CodeChunkerGitCommits."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create(self, commit_data: GitCommitSchema) -> CodeChunkerGitCommits:
        """Creates a new Git commit record."""
        with self.db_service.get_db() as session:
            db_record = CodeChunkerGitCommits(**commit_data.model_dump())
            session.add(db_record)
            session.commit()
            session.refresh(db_record)
            return db_record

    def get_by_hash(self, commit_hash: str) -> Optional[CodeChunkerGitCommits]:
        """Retrieves a commit record by its hash."""
        with self.db_service.get_db() as session:
            return (
                session.query(CodeChunkerGitCommits)
                .filter(CodeChunkerGitCommits.hash == commit_hash)
                .first()
            )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[CodeChunkerGitCommits]:
        """Retrieves all commit records with pagination."""
        with self.db_service.get_db() as session:
            return session.query(CodeChunkerGitCommits).offset(skip).limit(limit).all()
