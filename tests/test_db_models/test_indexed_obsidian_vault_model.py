"""
tests/test_db_models/test_indexed_obsidian_vault_model.py
Pytest tests for IndexedObsidianVaults SQLAlchemy model.
"""

from datetime import datetime, timezone

import pytest

from wembed_core.config import AppConfig
from wembed_core.database import DatabaseService
from wembed_core.models import IndexedObsidianVaults


class TestIndexedObsidianVaultsModel:
    """Test suite for IndexedObsidianVaults SQLAlchemy model."""

    @pytest.fixture
    def config(self, monkeypatch):
        """Fixture providing test configuration with in-memory SQLite database."""
        from unittest.mock import Mock

        config = Mock(spec=AppConfig)
        config.sqlalchemy_uri = "sqlite:///:memory:"
        config.debug = True
        config.host = "testhost"
        config.user = "testuser"
        return config

    @pytest.fixture
    def db_service(self, config):
        """Fixture providing initialized DatabaseService."""
        service = DatabaseService(config)
        service.init_db()
        return service

    @pytest.fixture
    def db_session(self, db_service):
        """Fixture providing a database session."""
        session_gen = db_service.get_db()
        session = next(session_gen)
        try:
            yield session
        finally:
            session.close()

    @pytest.fixture
    def valid_repo(self, config):
        """Test creating and retrieving an IndexedRepo record."""
        repo = IndexedObsidianVaults(
            vault_name="test-vault",
            host=config.host,
            root_path="C:/Users/testuser/projects/test-vault",
            files=[
                "C:/Users/testuser/projects/test-vault/file1.txt",
                "C:/Users/testuser/projects/test-vault/file2.txt",
            ],
            file_count=2,
            indexed_at=datetime.now(tz=timezone.utc),
        )
        return repo

    def test_indexed_vault_creation(self, db_session, valid_repo):
        """Test creating and retrieving an IndexedRepo record."""
        db_session.add(valid_repo)
        db_session.commit()

        retrieved = (
            db_session.query(IndexedObsidianVaults)
            .filter_by(vault_name="test-vault")
            .first()
        )

        assert retrieved is not None
        assert retrieved.vault_name == "test-vault"
        assert retrieved.host == "testhost"
        assert retrieved.root_path == "C:/Users/testuser/projects/test-vault"
        assert retrieved.files == [
            "C:/Users/testuser/projects/test-vault/file1.txt",
            "C:/Users/testuser/projects/test-vault/file2.txt",
        ]
        assert retrieved.file_count == 2
        assert isinstance(retrieved.indexed_at, datetime)
        db_session.close()

    def test_indexed_vault_missing_required_fields(self, db_session):
        """Test that missing required fields raise an exception."""
        incomplete_repo = IndexedObsidianVaults(
            # 'vault_name' is missing
            host="testhost",
            root_path="C:/Users/testuser/projects/test-vault",
            files=["C:/Users/testuser/projects/test-vault/file1.txt"],
            file_count=1,
            indexed_at=datetime.now(tz=timezone.utc),
        )

        with pytest.raises(Exception) as excinfo:
            db_session.add(incomplete_repo)
            db_session.commit()

        assert "NOT NULL constraint failed" in str(excinfo.value)
        db_session.close()

    def test_indexed_vault_nullable_fields(self, db_session):
        """Test that nullable fields can be set to None."""
        repo_with_nulls = IndexedObsidianVaults(
            vault_name="null-vault",
            host="None",  # noqa
            root_path="None",  # noqa
            file_count=0,
        )

        db_session.add(repo_with_nulls)
        db_session.commit()

        retrieved = (
            db_session.query(IndexedObsidianVaults)
            .filter_by(vault_name="null-vault")
            .first()
        )

        assert retrieved is not None
        assert retrieved.vault_name == "null-vault"
        assert retrieved.host == "None"
        assert retrieved.root_path == str("None")
        assert retrieved.files is None
        assert retrieved.file_count == 0
        assert retrieved.indexed_at is None
        db_session.close()
