"""
 wembed_core/models/indexing/indexed_obsidian_vaults.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 SQLAlchemy model for indexed Obsidian vaults.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class IndexedObsidianVaults(AppBase):
    """
    Represents a vault in the database.

    Attributes:
     - id (int): Primary key.
     - vault_name (str): Name of the vault.
     - host (str): Host of the vault (e.g., GitHub, GitLab).
     - root_path (str): Root path of the vault.
     - files (List[str], optional): List of file paths in the vault.
     - file_count (int): Number of files in the vault.
     - indexed_at (datetime, optional): Timestamp of the last indexing operation.
    """

    __tablename__ = "indexed_obsidian_vaults"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vault_name: Mapped[str] = mapped_column(String, nullable=False)
    host: Mapped[str] = mapped_column(String, nullable=False)
    root_path: Mapped[str] = mapped_column(String, nullable=False)
    files: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    file_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    indexed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
