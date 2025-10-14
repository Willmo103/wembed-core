"""
wembed_core/controllers/indexed_vault_controller.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Controller for CRUD operations on IndexedObsidianVaults.
"""

from typing import List, Optional

from wembed_core.database import DatabaseService
from wembed_core.models.indexing.indexed_obsidian_vaults import IndexedObsidianVaults
from wembed_core.schemas.indexing_schemas import IndexedObsidianVaultSchema


class IndexedVaultController:
    """Controller for CRUD operations on IndexedObsidianVaults."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create(self, vault_data: IndexedObsidianVaultSchema) -> IndexedObsidianVaults:
        """Creates a new indexed vault record."""
        with self.db_service.get_db() as session:
            db_record = IndexedObsidianVaults(**vault_data.model_dump())
            session.add(db_record)
            session.commit()
            session.refresh(db_record)
        return db_record

    def get_by_id(self, vault_id: int) -> Optional[IndexedObsidianVaults]:
        """Retrieves a vault by its ID."""
        with self.db_service.get_db() as session:
            res = (
                session.query(IndexedObsidianVaults)
                .filter(IndexedObsidianVaults.id == vault_id)
                .first()
            )
        return res

    def get_by_name(self, name: str) -> Optional[IndexedObsidianVaults]:
        """Retrieves a vault by its name."""
        with self.db_service.get_db() as session:
            res = (
                session.query(IndexedObsidianVaults)
                .filter(IndexedObsidianVaults.vault_name == name)
                .first()
            )
        return res

    def get_all(self, skip: int = 0, limit: int = 100) -> List[IndexedObsidianVaults]:
        """Retrieves all vaults with pagination."""
        with self.db_service.get_db() as session:
            res = session.query(IndexedObsidianVaults).offset(skip).limit(limit).all()
        return res

    def delete(self, vault_id: int) -> bool:
        """Deletes a vault record by its ID."""
        with self.db_service.get_db() as session:
            db_record = self.get_by_id(vault_id)
            if db_record:
                session.delete(db_record)
                session.commit()
                return True
            return False
