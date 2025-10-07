"""
tests/test_db_models/test_code_chunker_models.py

Unit tests for the Code Chunker related SQLAlchemy models.
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from sqlalchemy.orm.session import Session

from wembed_core import AppConfig
from wembed_core.database import DatabaseService
from wembed_core.models import (
    CodeChunkerCodeChunks,
    CodeChunkerDependencyNodes,
    CodeChunkerFunctionCalls,
    CodeChunkerGitBranches,
    CodeChunkerGitCommits,
    CodeChunkerGitFileInfo,
    CodeChunkerImportStatements,
    CodeChunkerUsageNodes,
)


class TestCodeChunkerModels:
    """Test suite for Code Chunker SQLAlchemy models."""

    @pytest.fixture
    def config(self) -> Mock:
        """Fixture providing test configuration with in-memory SQLite database."""
        config = Mock(spec=AppConfig)
        config.sqlalchemy_uri = "sqlite:///:memory:"
        config.debug = True
        config.host = "testhost"
        config.user = "testuser"
        return config

    @pytest.fixture
    def db_service(self, config: Mock) -> DatabaseService:
        """Fixture providing initialized DatabaseService."""
        service = DatabaseService(config)
        service.init_db()
        return service

    @pytest.fixture
    def db_session(self, db_service: DatabaseService) -> Session:
        """Fixture providing a database session."""
        session_gen = db_service.get_db()
        session = next(session_gen)
        try:
            yield session
        finally:
            session.close()

    def test_git_commit_crud(self, db_session: Session):
        """Tests CRUD for the CodeChunkerGitCommits model."""
        now = datetime.now(timezone.utc)
        record = CodeChunkerGitCommits(
            hash="c29bcb43a72bab21817329b2f7d3cf28a6fca8d2",
            author="Will Morris",
            date=now,
            message="feat: Add new models",
            files_changed=["models/code_chunker.py"],
            insertions=150,
            deletions=25,
        )
        db_session.add(record)
        db_session.commit()

        retrieved = (
            db_session.query(CodeChunkerGitCommits).filter_by(id=record.id).first()
        )
        assert retrieved is not None
        assert retrieved.author == "Will Morris"
        assert retrieved.insertions == 150

    def test_git_file_info_crud(self, db_session: Session):
        """Tests CRUD for the CodeChunkerGitFileInfo model."""
        now = datetime.now(timezone.utc)
        record = CodeChunkerGitFileInfo(
            file_path="src/main.py",
            last_commit_hash="c29bcb43a72bab21817329b2f7d3cf28a6fca8d2",
            last_author="Will Morris",
            last_modified=now,
            total_commits=10,
            contributors=["Will Morris", "Another Dev"],
            lines_added_total=500,
            lines_removed_total=100,
            creation_date=now,
        )
        db_session.add(record)
        db_session.commit()

        retrieved = (
            db_session.query(CodeChunkerGitFileInfo).filter_by(id=record.id).first()
        )
        assert retrieved is not None
        assert retrieved.total_commits == 10
        assert "Another Dev" in retrieved.contributors

    def test_git_branch_crud(self, db_session: Session):
        """Tests CRUD for the CodeChunkerGitBranches model."""
        now = datetime.now(timezone.utc)
        record = CodeChunkerGitBranches(
            name="main",
            last_commit="c29bcb43a72bab21817329b2f7d3cf28a6fca8d2",
            last_commit_date=now,
            is_current=True,
        )
        db_session.add(record)
        db_session.commit()

        retrieved = (
            db_session.query(CodeChunkerGitBranches).filter_by(id=record.id).first()
        )
        assert retrieved is not None
        assert retrieved.is_current is True

    def test_code_chunk_crud(self, db_session: Session):
        """Tests CRUD for the CodeChunkerCodeChunks model."""
        chunk_uuid = str(uuid.uuid4())
        record = CodeChunkerCodeChunks(
            chunk_uuid=chunk_uuid,
            content="def my_function():\n    pass",
            chunk_type="function",
            file_path="src/utils.py",
            start_line=10,
            end_line=11,
            dependencies=["os", "sys"],
            docstring="This is a docstring.",
        )
        db_session.add(record)
        db_session.commit()

        retrieved = (
            db_session.query(CodeChunkerCodeChunks).filter_by(id=record.id).first()
        )
        assert retrieved is not None
        assert retrieved.chunk_uuid == chunk_uuid
        assert retrieved.chunk_type == "function"

    def test_dependency_node_crud(self, db_session: Session):
        """Tests CRUD for the CodeChunkerDependencyNodes model."""
        record = CodeChunkerDependencyNodes(
            name="pytest",
            version="8.4.2",
            source="external",
            used_by=["tests/test_models.py"],
            imports=[],
        )
        db_session.add(record)
        db_session.commit()

        retrieved = (
            db_session.query(CodeChunkerDependencyNodes).filter_by(id=record.id).first()
        )
        assert retrieved is not None
        assert retrieved.name == "pytest"
        assert retrieved.version == "8.4.2"

    def test_import_statement_crud(self, db_session: Session):
        """Tests CRUD for the CodeChunkerImportStatements model."""
        record = CodeChunkerImportStatements(
            module="datetime",
            names=["datetime", "timezone"],
            file_path="src/utils.py",
            line_number=1,
            is_from_import=True,
        )
        db_session.add(record)
        db_session.commit()

        retrieved = (
            db_session.query(CodeChunkerImportStatements)
            .filter_by(id=record.id)
            .first()
        )
        assert retrieved is not None
        assert retrieved.module == "datetime"
        assert "timezone" in retrieved.names

    def test_usage_node_crud(self, db_session: Session):
        """Tests CRUD for the CodeChunkerUsageNodes model."""
        record = CodeChunkerUsageNodes(
            identifier="my_function",
            file_path="src/utils.py",
            node_type="function",
            start_line=10,
            end_line=11,
            complexity_score=1,
        )
        db_session.add(record)
        db_session.commit()

        retrieved = (
            db_session.query(CodeChunkerUsageNodes).filter_by(id=record.id).first()
        )
        assert retrieved is not None
        assert retrieved.identifier == "my_function"
        assert retrieved.complexity_score == 1

    def test_function_call_crud(self, db_session: Session):
        """Tests CRUD for the CodeChunkerFunctionCalls model."""
        record = CodeChunkerFunctionCalls(
            caller_file="src/main.py",
            caller_function="main",
            called_function="my_function",
            line_number=50,
            context="result = my_function()",
        )
        db_session.add(record)
        db_session.commit()

        retrieved = (
            db_session.query(CodeChunkerFunctionCalls).filter_by(id=record.id).first()
        )
        assert retrieved is not None
        assert retrieved.caller_function == "main"
        assert retrieved.called_function == "my_function"
