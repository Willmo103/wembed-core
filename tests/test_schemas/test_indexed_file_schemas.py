"""
tests/test_indexed_file_schemas.py
Pytest tests for HostFileSchema Pydantic model.
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from wembed_core.schemas.indexed_file_schema import IndexedFileSchema


class TestHostFileSchema:
    """Test suite for HostFileSchema Pydantic model."""

    def test_schema_creation_with_required_fields(self):
        """Test creating a HostFileSchema with only required fields."""
        schema = IndexedFileSchema(
            id="test-file-001",
            source_type="git",
            source_root="/home/user/project",
            source_name="test-repo",
        )

        assert schema.id == "test-file-001"
        assert schema.version == 1  # Default value
        assert schema.source_type == "git"
        assert schema.source_root == "/home/user/project"
        assert schema.source_name == "test-repo"

        # Optional fields should be None
        assert schema.host is None
        assert schema.user is None
        assert schema.content is None

        # Timestamps should be auto-generated
        assert isinstance(schema.created_at, datetime)
        assert isinstance(schema.updated_at, datetime)

    def test_schema_creation_with_all_fields(self):
        """Test creating a HostFileSchema with all fields populated."""
        now = datetime.now(timezone.utc)

        schema = IndexedFileSchema(
            id="full-file-001",
            version=2,
            source_type="local",
            source_root="/projects",
            source_name="my-project",
            host="localhost",
            user="testuser",
            name="example.py",
            stem="example",
            path="/projects/example.py",
            relative_path="example.py",
            suffix=".py",
            sha256="a" * 64,
            md5="b" * 32,
            mode=644,
            size=2048,
            content=b"print('hello')",
            content_text="print('hello')",
            ctime_iso=now,
            mtime_iso=now,
            line_count=1,
            uri="file:///projects/example.py",
            mimetype="text/x-python",
            created_at=now,
            updated_at=now,
        )

        assert schema.id == "full-file-001"
        assert schema.version == 2
        assert schema.name == "example.py"
        assert schema.stem == "example"
        assert schema.suffix == ".py"
        assert schema.size == 2048
        assert schema.content == b"print('hello')"
        assert schema.line_count == 1

    def test_bump_version_method(self):
        """Test that bump_version increments version and updates timestamp."""
        schema = IndexedFileSchema(
            id="version-test",
            source_type="git",
            source_root="/test",
            source_name="test-repo",
            version=1,
        )

        initial_version = schema.version
        initial_updated_at = schema.updated_at

        # Wait a tiny bit to ensure timestamp changes
        import time

        time.sleep(0.01)

        schema.bump_version()

        assert schema.version == initial_version + 1
        assert schema.updated_at > initial_updated_at

        # Bump again to verify it continues incrementing
        schema.bump_version()
        assert schema.version == initial_version + 2

    def test_schema_validation_errors(self):
        """Test that missing required fields raise ValidationError."""
        # Missing 'id' field
        with pytest.raises(ValidationError) as exc_info:
            IndexedFileSchema(
                source_type="git", source_root="/test", source_name="test-repo"
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("id",) for error in errors)

        # Missing 'source_type' field
        with pytest.raises(ValidationError) as exc_info:
            IndexedFileSchema(
                id="test-001", source_root="/test", source_name="test-repo"
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("source_type",) for error in errors)

    def test_schema_from_orm_compatibility(self):
        """Test that schema can be created from ORM model (from_attributes=True)."""
        from wembed_core.models.indexing.indexed_files import IndexedFiles

        # Create a mock ORM object
        now = datetime.now(timezone.utc)
        orm_record = IndexedFiles(
            id="orm-test-001",
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
            sha256="a" * 64,
            md5="b" * 32,
            mode=644,
            size=1024,
            content_text="print('hello')",
            ctime_iso=now,
            mtime_iso=now,
            line_count=1,
            uri="file:///home/user/project/test.py",
            mimetype="text/x-python",
            created_at=now,
            updated_at=now,
        )

        # Create schema from ORM model
        schema = IndexedFileSchema.model_validate(orm_record)

        assert schema.id == "orm-test-001"
        assert schema.source_type == "git"
        assert schema.name == "test.py"
        assert schema.size == 1024
        assert schema.content_text == "print('hello')"

    def test_schema_serialization(self):
        """Test that schema can be serialized to dict and JSON."""
        schema = IndexedFileSchema(
            id="serialize-test",
            source_type="local",
            source_root="/test",
            source_name="test-project",
            name="file.txt",
            size=100,
        )

        # Test dict serialization
        schema_dict = schema.model_dump()
        assert isinstance(schema_dict, dict)
        assert schema_dict["id"] == "serialize-test"
        assert schema_dict["name"] == "file.txt"
        assert schema_dict["size"] == 100

        # Test JSON serialization
        schema_json = schema.model_dump_json()
        assert isinstance(schema_json, str)
        assert '"id":"serialize-test"' in schema_json

        # Verify we can deserialize back
        deserialized = IndexedFileSchema.model_validate_json(schema_json)
        assert deserialized.id == schema.id
        assert deserialized.name == schema.name
