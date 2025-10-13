"""
wembed_core/controllers/code_chunker_git_file_info_controller.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Controller for CRUD operations on CodeChunkerGitFileInfo.
"""

from typing import Optional

from wembed_core.database import DatabaseService
from wembed_core.models import CodeChunkerGitFileInfo
from wembed_core.schemas import GitFileInfoSchema


class CodeChunkerGitFileInfoController:
    """Controller for CRUD operations on CodeChunkerGitFileInfo."""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def create(self, file_info_data: GitFileInfoSchema) -> CodeChunkerGitFileInfo:
        """Creates a new Git file info record."""
        with self.db_service.get_db() as session:
            db_record = CodeChunkerGitFileInfo(**file_info_data.model_dump())
            session.add(db_record)
            session.commit()
            session.refresh(db_record)
            return db_record

    def get_by_file_path(self, file_path: str) -> Optional[CodeChunkerGitFileInfo]:
        """Retrieves a file info record by its path."""
        with self.db_service.get_db() as session:
            return (
                session.query(CodeChunkerGitFileInfo)
                .filter(CodeChunkerGitFileInfo.file_path == file_path)
                .first()
            )

    def update(
        self, file_path: str, file_info_data: GitFileInfoSchema
    ) -> Optional[CodeChunkerGitFileInfo]:
        """Updates an existing file info record, identified by file_path."""
        with self.db_service.get_db() as session:
            db_record = (
                session.query(CodeChunkerGitFileInfo)
                .filter(CodeChunkerGitFileInfo.file_path == file_path)
                .first()
            )
            if db_record:
                update_data = file_info_data.model_dump(exclude_unset=True)
                for key, value in update_data.items():
                    setattr(db_record, key, value)
                session.commit()
                session.refresh(db_record)
            return db_record
