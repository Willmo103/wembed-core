"""
tests/test_db_models/test_indexed_repos_model.py
Pytest tests for IndexedRepos SQLAlchemy model.
"""

from datetime import datetime, timezone

import pytest

from wembed_core.config import AppConfig
from wembed_core.database import DatabaseService
from wembed_core.models import IndexedRepos


class TestIndexedReposModel:
    """Test suite for IndexedRepos SQLAlchemy model."""

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
        with db_service.get_db() as session:
            yield session

    @pytest.fixture
    def valid_repo(self, config):
        """Test creating and retrieving an IndexedRepo record."""
        repo = IndexedRepos(
            repo_name="test-repo",
            host=config.host,
            root_path="C:/Users/testuser/projects/test-repo",
            files=[
                "C:/Users/testuser/projects/test-repo/file1.txt",
                "C:/Users/testuser/projects/test-repo/file2.txt",
            ],
            file_count=2,
            indexed_at=datetime.now(tz=timezone.utc),
        )
        return repo

    def test_indexed_repo_creation(self, db_session, valid_repo):
        """Test creating and retrieving an IndexedRepo record."""
        db_session.add(valid_repo)
        db_session.commit()

        retrieved = (
            db_session.query(IndexedRepos).filter_by(repo_name="test-repo").first()
        )

        assert retrieved is not None
        assert retrieved.repo_name == "test-repo"
        assert retrieved.host == "testhost"
        assert retrieved.root_path == "C:/Users/testuser/projects/test-repo"
        assert retrieved.files == [
            "C:/Users/testuser/projects/test-repo/file1.txt",
            "C:/Users/testuser/projects/test-repo/file2.txt",
        ]
        assert retrieved.file_count == 2
        assert isinstance(retrieved.indexed_at, datetime)

    def test_indexed_repo_missing_required_fields(self, db_session):
        """Test that missing required fields raise an exception."""
        incomplete_repo = IndexedRepos(
            # 'repo_name' is missing
            host="testhost",
            root_path="C:/Users/testuser/projects/test-repo",
            files=["C:/Users/testuser/projects/test-repo/file1.txt"],
            file_count=1,
            indexed_at=datetime.now(tz=timezone.utc),
        )

        with pytest.raises(Exception) as excinfo:
            db_session.add(incomplete_repo)
            db_session.commit()

        assert "NOT NULL constraint failed" in str(excinfo.value)

    def test_indexed_repo_nullable_fields(self, db_session):
        """Test that nullable fields can be set to None."""
        repo_with_nulls = IndexedRepos(
            repo_name="null-repo",
            host="None",  # noqa
            root_path="None",  # noqa
            file_count=0,
        )

        db_session.add(repo_with_nulls)
        db_session.commit()

        retrieved = (
            db_session.query(IndexedRepos).filter_by(repo_name="null-repo").first()
        )

        assert retrieved is not None
        assert retrieved.repo_name == "null-repo"
        assert retrieved.host == "None"
        assert retrieved.root_path == str("None")
        assert retrieved.files is None
        assert retrieved.file_count == 0
        assert retrieved.indexed_at is None
