"""
tests/test_database.py
Pytest tests for DatabaseService and HostFilesRecord model.
"""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from wembed_core.config import AppConfig
from wembed_core.database import DatabaseService
from wembed_core.models import IndexedFiles


class TestDatabaseAndFileRecord:
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
        yield session
        session.close()

    def test_database_initialization(self, config):
        """Test that DatabaseService initializes correctly."""
        db_service = DatabaseService(config)

        assert db_service.engine is None
        assert db_service.SessionLocal is None

        db_service.init_db()

        assert db_service.engine is not None
        assert db_service.SessionLocal is not None
        assert db_service.is_initialized is True

        # Re-initializing should not change the state
        db_service.init_db()

        assert db_service.is_initialized is True

    def test_calling_session_before_init_raises(self, config):
        """Test that calling get_db() before init_db() raises an exception."""
        db_service = DatabaseService(config)

        with pytest.raises(Exception) as excinfo:
            next(db_service.get_db())

        assert "Database not initialized" in str(excinfo.value)

    def test_create_and_query_file_record(self, db_session):
        """Test creating and querying a HostFilesRecord."""
        now = datetime.now()

        # Create a test record
        test_record = IndexedFiles(
            id="test-file-001",
            version=1,
            source_type="git",
            source_root="/home/user/project",
            source_name="test-repo",
            host="localhost",
            user="testuser",
            name="test.py",
            stem="test",
            path="/home/user/project/test.py",
            relative_path="test.py",
            suffix=".py",
            sha256="a" * 64,  # Mock SHA-256 hash
            md5="b" * 32,  # Mock MD5 hash
            mode=644,
            size=1024,
            content_text="print('hello world')",
            ctime_iso=datetime(2024, 1, 1, 12, 0, 0),
            mtime_iso=datetime(2024, 1, 1, 12, 0, 0),
            line_count=1,
            uri="file:///home/user/project/test.py",
            mimetype="text/x-python",
            created_at=now,
            updated_at=now,
        )

        db_session.add(test_record)
        db_session.commit()

        # Query the record back
        retrieved = db_session.query(IndexedFiles).filter_by(id="test-file-001").first()

        assert retrieved is not None
        assert retrieved.id == "test-file-001"
        assert retrieved.name == "test.py"
        assert retrieved.source_type == "git"
        assert retrieved.size == 1024

    def test_unique_sha256_constraint(self, db_session):
        """Test that sha256 field enforces uniqueness."""
        now = datetime.now()

        # Create first record
        record1 = IndexedFiles(
            id="file-001",
            version=1,
            source_type="local",
            source_root="/test",
            source_name="test",
            host="localhost",
            user="user1",
            name="file1.txt",
            stem="file1",
            path="/test/file1.txt",
            relative_path="file1.txt",
            suffix=".txt",
            sha256="unique-hash-123",
            md5="md5-hash-123",
            mode=644,
            size=100,
            content_text="content",
            ctime_iso=now,
            mtime_iso=now,
            line_count=1,
            uri="file:///test/file1.txt",
            mimetype="text/plain",
            created_at=now,
            updated_at=now,
        )

        db_session.add(record1)
        db_session.commit()

        # Attempt to create second record with same sha256
        record2 = IndexedFiles(
            id="file-002",
            version=1,
            source_type="local",
            source_root="/test",
            source_name="test",
            host="localhost",
            user="user2",
            name="file2.txt",
            stem="file2",
            path="/test/file2.txt",
            relative_path="file2.txt",
            suffix=".txt",
            sha256="unique-hash-123",  # Same SHA256
            md5="md5-hash-456",
            mode=644,
            size=200,
            content_text="different content",
            ctime_iso=now,
            mtime_iso=now,
            line_count=1,
            uri="file:///test/file2.txt",
            mimetype="text/plain",
            created_at=now,
            updated_at=now,
        )

        db_session.add(record2)

        # Should raise an integrity error due to unique constraint
        with pytest.raises(Exception):  # SQLAlchemy will raise IntegrityError
            db_session.commit()

    def test_database_session_generator(self, db_service):
        """Test that get_db() provides a working session generator."""
        session_gen = db_service.get_db()
        session = next(session_gen)

        assert session is not None

        # Verify we can use the session
        result = session.query(IndexedFiles).all()
        assert isinstance(result, list)

        session.close()

    def test_optional_content_field(self, db_session):
        """Test that the optional content field can be None or contain binary data."""
        now = datetime.now()

        # Test with None content
        record_without_content = IndexedFiles(
            id="no-content-file",
            version=1,
            source_type="local",
            source_root="/test",
            source_name="test",
            host="localhost",
            user="user",
            name="empty.txt",
            stem="empty",
            path="/test/empty.txt",
            relative_path="empty.txt",
            suffix=".txt",
            sha256="hash-no-content",
            md5="md5-no-content",
            mode=644,
            size=0,
            content=None,  # Explicitly None
            content_text="",
            ctime_iso=now,
            mtime_iso=now,
            line_count=0,
            uri="file:///test/empty.txt",
            mimetype="text/plain",
            created_at=now,
            updated_at=now,
        )

        db_session.add(record_without_content)
        db_session.commit()

        retrieved = (
            db_session.query(IndexedFiles).filter_by(id="no-content-file").first()
        )
        assert retrieved.content is None

        # Test with binary content
        binary_data = b"\x00\x01\x02\x03\xff"
        record_with_content = IndexedFiles(
            id="binary-content-file",
            version=1,
            source_type="local",
            source_root="/test",
            source_name="test",
            host="localhost",
            user="user",
            name="binary.dat",
            stem="binary",
            path="/test/binary.dat",
            relative_path="binary.dat",
            suffix=".dat",
            sha256="hash-with-content",
            md5="md5-with-content",
            mode=644,
            size=5,
            content=binary_data,
            content_text="",
            ctime_iso=now,
            mtime_iso=now,
            line_count=0,
            uri="file:///test/binary.dat",
            mimetype="application/octet-stream",
            created_at=now,
            updated_at=now,
        )

        db_session.add(record_with_content)
        db_session.commit()

        retrieved_binary = (
            db_session.query(IndexedFiles).filter_by(id="binary-content-file").first()
        )
        assert retrieved_binary.content == binary_data
