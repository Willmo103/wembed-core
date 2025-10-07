"""
tests/test_dl_docs_controllers.py

Tests for the Data Loading (DL) controllers, ensuring database
functionalities and relationships between Inputs, Documents, and Chunks.
"""

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest
from sqlalchemy.orm.session import Session

from wembed_core.config import AppConfig
from wembed_core.controllers import (
    DLChunkController,
    DLDocumentController,
    DLInputController,
)
from wembed_core.database import DatabaseService
from wembed_core.schemas.dl_schemas import (
    DLChunkSchema,
    DLDocumentSchema,
    DLInputSchema,
)


class TestDLControllers:
    """Test suite for DL-related controllers."""

    # region Fixtures
    @pytest.fixture
    def config(self) -> Mock:
        """Fixture for a mock AppConfig with an in-memory SQLite database."""
        config = Mock(spec=AppConfig)
        config.sqlalchemy_uri = "sqlite:///:memory:"
        config.debug = True
        return config

    @pytest.fixture
    def db_service(self, config: Mock) -> DatabaseService:
        """Fixture for an initialized DatabaseService."""
        service = DatabaseService(config)
        service.init_db()
        return service

    @pytest.fixture
    def db_session(self, db_service: DatabaseService):
        """Fixture providing a database session."""

        # NEW, CORRECT WAY:
        with db_service.get_db() as session:
            yield session

    @pytest.fixture
    def dl_input_controller(self, db_service: DatabaseService) -> DLInputController:
        """Fixture to provide an instance of the DLInputController."""
        return DLInputController(db_service)

    @pytest.fixture
    def dl_document_controller(
        self, db_service: DatabaseService
    ) -> DLDocumentController:
        """Fixture to provide an instance of the DLDocumentController."""
        return DLDocumentController(db_service)

    @pytest.fixture
    def dl_chunk_controller(self, db_service: DatabaseService) -> DLChunkController:
        """Fixture to provide an instance of the DLChunkController."""
        return DLChunkController(db_service)

    @pytest.fixture
    def sample_input_schema(self) -> DLInputSchema:
        """Provides a sample DLInputSchema object for testing."""
        return DLInputSchema(
            source="test_source_001",
            source_ref="test_ref_001",
            source_type="test",
            status=100,
        )

    @pytest.fixture
    def sample_document_schema(self) -> DLDocumentSchema:
        """Provides a sample DLDocumentSchema object for testing."""
        return DLDocumentSchema(
            source="/path/to/test.txt",
            source_type="file",
            source_ref="1",
            markdown="# Test",
            html="<h1>Test</h1>",
            text="Test",
        )

    # endregion

    def test_create_and_get_input(
        self,
        dl_input_controller: DLInputController,
        sample_input_schema: DLInputSchema,
    ):
        """Tests basic creation and retrieval of a DLInput record."""
        # Create
        created_input = dl_input_controller.create(sample_input_schema)
        assert created_input is not None
        assert created_input.id is not None
        assert created_input.source_ref == "test_ref_001"

        # Retrieve
        retrieved_input = dl_input_controller.get_by_id(created_input.id)
        assert retrieved_input is not None
        assert retrieved_input.id == created_input.id

    def test_create_and_get_document(
        self,
        dl_document_controller: DLDocumentController,
        sample_document_schema: DLDocumentSchema,
    ):
        """Tests basic creation and retrieval of a DLDocument record."""
        # Create
        created_doc = dl_document_controller.create(sample_document_schema)
        assert created_doc is not None
        assert created_doc.id is not None
        assert created_doc.source == "/path/to/test.txt"

        # Retrieve
        retrieved_doc = dl_document_controller.get_by_id(created_doc.id)
        assert retrieved_doc is not None
        assert retrieved_doc.id == created_doc.id

    def test_full_relationship_flow(
        self,
        dl_input_controller: DLInputController,
        dl_document_controller: DLDocumentController,
        dl_chunk_controller: DLChunkController,
    ):
        """
        Tests the full relational workflow from Input -> Document -> Chunks.
        """
        # 1. Create an initial Input record
        input_schema = DLInputSchema(
            source="workflow_source_001",  # <-- ADD THIS
            source_ref="workflow_ref_001",
            source_type="workflow",
            status=100,
        )
        created_input = dl_input_controller.create(input_schema)
        assert created_input.status == 100

        # 2. Create a Document that refers to the Input
        doc_schema = DLDocumentSchema(
            source="/path/workflow.txt",
            source_type="file",
            source_ref=str(created_input.id),
            markdown="# Workflow",
            html="",
            text="Workflow",
        )
        created_doc = dl_document_controller.create(doc_schema)
        assert created_doc.source_ref == str(created_input.id)

        # 3. Update the Input to link to the new Document and mark as processed
        updated_input_schema = DLInputSchema.model_validate(created_input)
        updated_input_schema.status = 200  # Processed
        updated_input_schema.output_doc_id = created_doc.id
        dl_input_controller.update(created_input.id, updated_input_schema)

        # Verify the update
        retrieved_input = dl_input_controller.get_by_id(created_input.id)
        assert retrieved_input.status == 200
        assert retrieved_input.output_doc_id == created_doc.id

        # 4. Create Chunks that belong to the Document
        chunk_schemas = [
            DLChunkSchema(
                document_id=created_doc.id,
                chunk_index=i,
                text_chunk=f"This is chunk {i}",
                embedding=[0.1 * i] * 8,
            )
            for i in range(3)
        ]
        created_chunks = dl_chunk_controller.create_batch(chunk_schemas)
        assert len(created_chunks) == 3

        # 5. Verify the Chunks are correctly associated
        retrieved_chunks = dl_chunk_controller.get_by_document_id(created_doc.id)
        assert len(retrieved_chunks) == 3
        assert retrieved_chunks[0].chunk_index == 0
        assert retrieved_chunks[1].text_chunk == "This is chunk 1"
        assert retrieved_chunks[2].document_id == created_doc.id

    def test_delete_operations(
        self,
        dl_document_controller: DLDocumentController,
        dl_chunk_controller: DLChunkController,
    ):
        """Tests deletion logic, particularly deleting chunks by document ID."""
        # 1. Create a parent document
        doc_schema = DLDocumentSchema(
            source="/path/to/delete.txt",
            source_type="file",
            source_ref="delete_ref",
            markdown="",
            html="",
            text="",
        )
        created_doc = dl_document_controller.create(doc_schema)

        chunk_schemas = [
            DLChunkSchema(
                document_id=created_doc.id,
                idx=i,  # <-- FIX: Changed from chunk_index to idx
                text_chunk=f"Chunk {i}",
                embedding=[0.1] * 8,
            )
            for i in range(5)
        ]

        dl_chunk_controller.create_batch(chunk_schemas)

        # Verify chunks exist
        assert len(dl_chunk_controller.get_by_document_id(created_doc.id)) == 5

        # 3. Delete chunks by document ID
        deleted_count = dl_chunk_controller.delete_by_document_id(created_doc.id)
        assert deleted_count == 5

        # Verify chunks are gone
        assert len(dl_chunk_controller.get_by_document_id(created_doc.id)) == 0

        # 4. Delete the parent document
        delete_success = dl_document_controller.delete(created_doc.id)
        assert delete_success is True
        assert dl_document_controller.get_by_id(created_doc.id) is None
