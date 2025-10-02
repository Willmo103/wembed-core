"""
tests/test_schemas/test_indexed_repo_schema.py
Pytest tests for IndexedRepoSchema Pydantic model.
"""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from wembed_core.schemas import IndexedRepoSchema


class TestIndexedRepoSchema:
    """Test suite for IndexedRepoSchema Pydantic model."""

    def test_valid_indexed_repo_schema(self):
        """Test creating a valid IndexedRepoSchema instance."""
        indexed_at = datetime.now(tz=timezone.utc) - timedelta(days=1)
        repo = IndexedRepoSchema(
            id=1,
            name="test-repo",
            host="github.com",
            root_path="/path/to/repo",
            files=["/path/to/repo/file1.txt", "/path/to/repo/file2.txt"],
            file_count=2,
            indexed_at=indexed_at,
        )
        assert repo.id == 1
        assert repo.name == "test-repo"
        assert repo.host == "github.com"
        assert repo.root_path == "/path/to/repo"
        assert repo.files == ["/path/to/repo/file1.txt", "/path/to/repo/file2.txt"]
        assert repo.file_count == 2
        assert repo.indexed_at == indexed_at

    def test_missing_required_fields(self):
        """Test that missing required fields raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            IndexedRepoSchema(
                host="github.com",
                root_path="/path/to/repo",
                file_count=2,
            )
        errors = exc_info.value.errors()
        assert any(error for error in errors)

    # def test_invalid_file_count(self):
    #     """Test that negative file_count raises ValidationError."""
    #     with pytest.raises(ValidationError) as exc_info:
    #         IndexedRepoSchema(
    #             name="test-repo",
    #             host="github.com",
    #             root_path="/path/to/repo",
    #             file_count=-1,
    #         )
    #     errors = exc_info.value.errors()
    #     assert any(
    #         error["loc"] == ("file_count",)
    #         and error["type"] == "value_error.number.not_ge"
    #         for error in errors
    #     )

    def test_optional_fields(self):
        """Test that optional fields can be omitted."""
        repo = IndexedRepoSchema(
            name="test-repo",
            host="github.com",
            root_path="/path/to/repo",
            file_count=0,
        )
        assert repo.id is None
        assert repo.files is None
        assert repo.indexed_at is None
