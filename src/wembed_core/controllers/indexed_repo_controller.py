"""
wembed_core/controllers/indexed_repo_controller.py
"""

from typing import List, Optional

from wembed_core.database import DatabaseService
from wembed_core.models.indexed_repos import IndexedRepos
from wembed_core.schemas.indexed_repo_schema import IndexedRepoSchema


class IndexedRepoController:
    """Controller for CRUD operations on IndexedRepos."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create(self, repo_data: IndexedRepoSchema) -> IndexedRepos:
        """Creates a new indexed repository record."""
        with self.db_service.get_db() as session:
            db_record = IndexedRepos(**repo_data.model_dump())
            session.add(db_record)
            session.commit()
            session.refresh(db_record)
            return db_record

    def get_by_id(self, repo_id: int) -> Optional[IndexedRepos]:
        """Retrieves a repository by its ID."""
        with self.db_service.get_db() as session:
            return (
                session.query(IndexedRepos).filter(IndexedRepos.id == repo_id).first()
            )

    def get_by_name(self, name: str) -> Optional[IndexedRepos]:
        """Retrieves a repository by its name."""
        with self.db_service.get_db() as session:
            return (
                session.query(IndexedRepos)
                .filter(IndexedRepos.repo_name == name)
                .first()
            )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[IndexedRepos]:
        """Retrieves all repositories with pagination."""
        with self.db_service.get_db() as session:
            return session.query(IndexedRepos).offset(skip).limit(limit).all()

    def delete(self, repo_id: int) -> bool:
        """Deletes a repository record by its ID."""
        with self.db_service.get_db() as session:
            db_record = self.get_by_id(repo_id)
            if db_record:
                session.delete(db_record)
                session.commit()
                return True
            return False
