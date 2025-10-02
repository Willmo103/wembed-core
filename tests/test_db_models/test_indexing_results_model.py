"""
tests/test_database.py
Pytest tests for DatabaseService and HostFilesRecord model.
"""

from datetime import datetime

import pytest

from wembed_core.config import AppConfig
from wembed_core.database import AppBase, DatabaseService
from wembed_core.models.indexing_results import FileIndexingResults


class TestScanResultRecord:
    """Test suite for DatabaseService and HostFilesRecord model."""

    @pytest.fixture
    def config(self, monkeypatch):
        """Fixture providing test configuration with in-memory SQLite database."""
        # Mock the config to use in-memory SQLite for testing
        from unittest.mock import Mock

        config = Mock(spec=AppConfig)
        config.sqlalchemy_uri = "sqlite:///:memory:"
        config.environment = "development"
        return config

    def test_scan_result_record_creation(self, config):
        """Test creating and retrieving a FileIndexResult."""
        db_service = DatabaseService(config)
        db_service.init_db()

        # Create a new database session
        session_gen = db_service.get_db()
        session = next(session_gen)

        # Create a new FileIndexResult
        scan_result = FileIndexingResults(
            id="scan123",
            root_path="/path/to/scan",
            scan_type="full",
            scan_name="Repo",
            files=["/path/to/scan/file1.txt", "/path/to/scan/file2.txt"],
            scan_start=datetime.now(),
            scan_end=datetime.now(),
            duration=300.0,
            options={"recursive": True, "follow_symlinks": False},
            user="testuser",
            host="testhost",
        )

        session.add(scan_result)
        session.commit()

        # Retrieve the FileIndexResult
        retrieved = session.query(FileIndexingResults).filter_by(id="scan123").first()

        assert retrieved is not None
        assert retrieved.id == "scan123"
        assert retrieved.root_path == "/path/to/scan"
        assert retrieved.scan_type == "full"
        assert retrieved.scan_name == "Repo"
        assert retrieved.files == ["/path/to/scan/file1.txt", "/path/to/scan/file2.txt"]
        assert retrieved.duration == 300.0
        assert retrieved.options == {"recursive": True, "follow_symlinks": False}
        assert retrieved.user == "testuser"
        assert retrieved.host == "testhost"

        # Close the session
        session.close()

    def test_nullable_fields(self, config):
        """Test that nullable fields can be set to None."""
        db_service = DatabaseService(config)
        db_service.init_db()

        # Create a new database session
        session_gen = db_service.get_db()
        session = next(session_gen)

        # Create a new FileIndexResult with nullable fields set to None
        scan_result = FileIndexingResults(
            id="scan124",
            root_path="/path/to/scan",
            scan_type="incremental",
            scan_name=None,
            files=None,
            scan_start=datetime.now(),
            scan_end=None,
            duration=None,
            options=None,
            user="testuser",
            host="testhost",
        )

        session.add(scan_result)
        session.commit()

        # Retrieve the FileIndexResult
        retrieved = session.query(FileIndexingResults).filter_by(id="scan124").first()

        assert retrieved is not None
        assert retrieved.id == "scan124"
        assert retrieved.scan_name is None
        assert retrieved.files is None
        assert retrieved.scan_end is None
        assert retrieved.duration is None
        assert retrieved.options is None

        # Close the session
        session.close()
