"""
tests/test_db_models/test_dl_models.py

Unit tests for the DLInputs, DLDocuments, and DLChunks SQLAlchemy models.
"""

from datetime import datetime, timedelta, timezone

import pytest

from wembed_core import AppConfig
from wembed_core.database import DatabaseService
from wembed_core.models.dl_doc.dl_doc_chunks import DLChunks
from wembed_core.models.dl_doc.dl_documents import DLDocuments
from wembed_core.models.dl_doc.dl_inputs import DLInputs


class TestDLModels:

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

    def test_dl_models_crud(self, db_session, config):
        """Test CRUD operations for DL models."""
        # Create a DLInputs record
        from datetime import datetime

        input_record = DLInputs(
            id=1,
            source_ref="1",
            source_type="test",
            status=100,
            errors=["failed to process"],
            added_at=datetime.now(timezone.utc) - timedelta(days=1),
            processed_at=None,
            output_doc_id=None,
        )
        db_session.add(input_record)
        db_session.commit()
        db_session.refresh(input_record)
        assert input_record.id == 1
        assert input_record.source_ref == "1"
        assert input_record.status == 100

        # Create a DLDocuments record
        doc_record = DLDocuments(
            id=1,
            source="test source",
            source_type="test",
            source_ref=input_record.id,
            dl_doc=None,
            markdown="# Test Document",
            html="<p>test</p>",
            text="test",
            doctags=None,
            chunks_json=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(doc_record)
        db_session.commit()
        db_session.refresh(doc_record)
        assert doc_record.id == 1
        assert doc_record.source_ref == input_record.id
        assert doc_record.markdown == "# Test Document"
        assert doc_record.html == "<p>test</p>"
        assert doc_record.text == "test"
        assert doc_record.doctags is None
        assert doc_record.chunks_json is None
        db_session.close()

    def test_dl_chunks_crud(self, db_session, config):
        """Test CRUD operations for DLChunks model."""
        # Create a DLChunks record
        chunk_record = DLChunks(
            id=1,
            document_id=1,
            chunk_index=0,
            chunk_text="This is a test chunk.",
            embedding=[0.1] * 768,  # Mock embedding vector
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(chunk_record)
        db_session.commit()
        db_session.refresh(chunk_record)
        assert chunk_record.id == 1
        assert chunk_record.document_id == 1
        assert chunk_record.chunk_index == 0
        assert chunk_record.chunk_text == "This is a test chunk."
        assert len(chunk_record.embedding) == 768
        db_session.close()

    def test_relationships(self, db_session, config):
        """Test relationships between DLInputs, DLDocuments, and DLChunks."""
        from datetime import datetime

        # Create DLInputs record
        input_record = DLInputs(
            id=1,
            source_ref="1",
            source_type="test",
            status=100,
            errors=None,
            added_at=datetime.now(timezone.utc) - timedelta(days=1),
            processed_at=None,
            output_doc_id=None,
        )
        db_session.add(input_record)
        db_session.commit()
        db_session.refresh(input_record)

        # Create DLDocuments record linked to DLInputs
        doc_record = DLDocuments(
            id=1,
            source="test source",
            source_type="test",
            source_ref=input_record.id,
            dl_doc=None,
            markdown="# Test Document",
            html="<p>test</p>",
            text="test",
            doctags=None,
            chunks_json=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db_session.add(doc_record)
        db_session.commit()
        db_session.refresh(doc_record)

        # Create DLChunks record linked to DLDocuments
        chunk_record = DLChunks(
            id=1,
            document_id=doc_record.id,
            chunk_index=0,
            chunk_text="This is a test chunk.",
            embedding=[0.1] * 768,  # Mock embedding vector
            created_at=datetime.now(timezone.utc),
        )
        db_session.add(chunk_record)
        db_session.commit()
        db_session.refresh(chunk_record)

        # Verify relationships
        assert chunk_record.document_id == doc_record.id
        assert doc_record.source_ref == input_record.id
        assert input_record.id == 1
        assert doc_record.id == 1
        assert chunk_record.id == 1
        assert chunk_record.chunk_text == "This is a test chunk."
        assert doc_record.markdown == "# Test Document"
        assert input_record.status == 100
        db_session.close()
