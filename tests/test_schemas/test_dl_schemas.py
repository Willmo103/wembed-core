from datetime import datetime, timedelta, timezone

import pytest

from wembed_core.schemas.dl_schemas import (
    DLChunkSchema,
    DLDocumentSchema,
    DLInputSchema,
)


class TestDLSchemas:
    def test_dl_chunk_schema(self):
        """Test DLChunkSchema creation and attribute access."""
        chunk_data = {
            "id": 1,
            "document_id": 10,
            "idx": 0,
            "text_chunk": "This is a test chunk.",
            "embedding": [0.1, 0.2, 0.3],
            "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
        }
        chunk = DLChunkSchema(**chunk_data)
        assert chunk.id == 1
        assert chunk.document_id == 10
        assert chunk.idx == 0
        assert chunk.text_chunk == "This is a test chunk."
        assert chunk.embedding == [0.1, 0.2, 0.3]
        assert chunk.created_at == datetime(2024, 1, 1, tzinfo=timezone.utc)

    def test_dl_document_schema(self):
        """Test DLDocumentSchema creation and attribute access."""
        doc_data = {
            "id": 5,
            "source": "test_source",
            "source_type": "file",
            "source_ref": "ref_123",
            "dl_doc": None,
            "markdown": "# Test Document",
            "html": "<h1>Test Document</h1>",
            "text": "This is the text of the document.",
            "doctags": None,
            "chunks_json": [],
            "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
            "updated_at": None,
        }
        document = DLDocumentSchema(**doc_data)
        assert document.id == 5
        assert document.source == "test_source"
        assert document.source_type == "file"
        assert document.source_ref == "ref_123"
        assert document.dl_doc is None
        assert document.markdown == "# Test Document"
        assert document.html == "<h1>Test Document</h1>"
        assert document.text == "This is the text of the document."
        assert document.doctags is None

        assert document.chunks_json == []
        assert document.created_at == datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert document.updated_at is None

    def test_dl_input_schema(self):
        """Test DLInputSchema creation and attribute access."""
        input_data = {
            "id": 3,
            "source": "input_source",
            "source_ref": "ref_456",
            "source_type": "url",
            "status": 200,
            "errors": ["Error 1", "Error 2"],
            "added_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
            "processed_at": None,
            "output_doc_id": None,
        }
        dl_input = DLInputSchema(**input_data)
        assert dl_input.id == 3
        assert dl_input.source == "input_source"
        assert dl_input.source_ref == "ref_456"
        assert dl_input.source_type == "url"
        assert dl_input.status == 200
        assert dl_input.errors == ["Error 1", "Error 2"]
        assert dl_input.added_at == datetime(2024, 1, 1, tzinfo=timezone.utc)
        assert dl_input.processed_at is None
        assert dl_input.output_doc_id is None
