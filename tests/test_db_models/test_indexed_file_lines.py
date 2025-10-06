"""
tests/test_db_models/test_indexed_file_lines.py
Unit tests for the IndexedFileLines SQLAlchemy model.
"""

from datetime import datetime
from unittest.mock import Mock

import pytest

from wembed_core.config import AppConfig
from wembed_core.database import AppBase, DatabaseService
from wembed_core.models.indexed_file_lines import IndexedFileLines
from wembed_core.models.indexed_files import IndexedFiles


class TestIndexedFileLines:
    """Unit tests for the IndexedFileLines model."""

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
    def mock_file_record(self, db_session):
        """Fixture to create a mock IndexedFiles record in the database."""
        now = datetime.now()
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
            content_text="first line\nsecond line\n",
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

        retrieved = db_session.query(IndexedFiles).filter_by(id="test-file-001").first()
        return IndexedFiles(
            **retrieved.__dict__
        )  # Return a new instance to avoid session issues

        # Query the record back

    def test_model_create(self, db_session, mock_file_record):
        """Test creating an IndexedFileLines record."""
        now = datetime.now()

        # Create a test record
        test_line = IndexedFileLines(
            file_id=str(mock_file_record.id),
            line_number=1,
            line_text="first line",
            created_at=now,
        )
        db_session.add(test_line)
        db_session.commit()

        # Query the record back
        retrieved = (
            db_session.query(IndexedFileLines)
            .filter_by(file_id=mock_file_record.id, line_number=1)
            .first()
        )

        assert retrieved is not None
        assert retrieved.file_id == mock_file_record.id
        assert retrieved.line_number == 1
        assert retrieved.line_text == "first line"
        assert isinstance(retrieved.created_at, datetime)

    def test_model_constraints(self, db_session, mock_file_record):
        """Test constraints on the IndexedFileLines model."""
        now = datetime.now()

        # Create a test record with invalid line_number (negative)
        invalid_line = IndexedFileLines(
            file_id=mock_file_record.id,
            line_number=-1,
            line_text="Invalid line number",
            created_at=now,
        )

        db_session.add(invalid_line)
        with pytest.raises(Exception):
            db_session.commit()
        db_session.rollback()

        # Create a test record with missing required fields
        incomplete_line = IndexedFileLines(
            file_id=None,  # Missing file_id  # noqa
            line_number=2,
            line_text="Missing file_id",
            created_at=now,
        )

        db_session.add(incomplete_line)
        with pytest.raises(Exception):
            db_session.commit()
        db_session.rollback()

        # Create a test record with duplicate (file_id, line_number)
        valid_line = IndexedFileLines(
            file_id=mock_file_record.id,
            line_number=1,
            line_text="Duplicate line number",
            created_at=now,
        )
        db_session.add(valid_line)
        with pytest.raises(Exception):
            db_session.commit()
        db_session.rollback()

    def test_model_relationship(self, db_session, mock_file_record):
        """Test relationship between IndexedFileLines and IndexedFiles."""
        now = datetime.now()

        # Create multiple lines for the same file
        line1 = IndexedFileLines(
            file_id=mock_file_record.id,
            line_number=1,
            line_text="First line",
            created_at=now,
        )
        line2 = IndexedFileLines(
            file_id=mock_file_record.id,
            line_number=2,
            line_text="Second line",
            created_at=now,
        )
        db_session.add_all([line1, line2])
        db_session.commit()

        # Query the file and check its lines
        retrieved_file = (
            db_session.query(IndexedFiles).filter_by(id=mock_file_record.id).first()
        )

        assert retrieved_file is not None
        assert len(retrieved_file.lines) == 2
        assert retrieved_file.lines[0].line_text == "First line"
        assert retrieved_file.lines[1].line_text == "Second line"
