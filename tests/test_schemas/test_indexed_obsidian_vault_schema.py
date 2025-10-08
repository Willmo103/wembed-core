"""
tests/test_schemas/test_indexed_obsidian_vault_schema.py
Pytest tests for IndexedRepoSchema Pydantic model.
"""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from wembed_core.schemas import IndexedObsidianVaultSchema


class TestIndexedObsidianVaultSchema:
    """Tests for IndexedObsidianVaultSchema Pydantic model."""

    def test_valid_obsidian_vault_schema(self):
        """Test that valid data passes validation."""
        indexed_at = datetime.now(tz=timezone.utc) - timedelta(days=1)
        valid_data = IndexedObsidianVaultSchema(
            id=1,
            vault_name="MyVault",
            host="GitHub",
            root_path="/path/to/vault",
            files=["/path/to/vault/file1.md", "/path/to/vault/file2.md"],
            file_count=2,
            indexed_at=indexed_at,
        ).model_dump()

        schema = IndexedObsidianVaultSchema(**valid_data)
        assert schema.id == 1
        assert schema.vault_name == "MyVault"
        assert schema.host == "GitHub"
        assert schema.root_path == "/path/to/vault"
        assert schema.files == ["/path/to/vault/file1.md", "/path/to/vault/file2.md"]
        assert schema.file_count == 2
        assert schema.indexed_at == indexed_at

    def test_missing_required_fields(self):
        """Test that missing required fields raise ValidationError."""
        invalid_data = {
            "id": 1,
            # Missing 'vault_name'
            "host": "GitHub",
            "root_path": "/path/to/vault",
            "file_count": 2,
        }
        with pytest.raises(ValidationError) as exc_info:
            IndexedObsidianVaultSchema(**invalid_data)
        errors = exc_info.value.errors()
        assert any(error for error in errors)

    def test_invalid_field_types(self):
        """Test that invalid field types raise ValidationError."""
        invalid_data = {
            "id": "one",  # Should be int
            "vault_name": "MyVault",
            "host": "GitHub",
            "root_path": "/path/to/vault",
            "files": "not a list",  # Should be List[str]
            "file_count": "two",  # Should be int
            "indexed_at": "not a datetime",  # Should be datetime
        }
        with pytest.raises(ValidationError) as exc_info:
            IndexedObsidianVaultSchema(**invalid_data)
        errors = exc_info.value.errors()
        assert any(error for error in errors)

    def test_optional_fields(self):
        """Test that optional fields can be omitted."""
        valid_data = {
            "vault_name": "MyVault",
            "host": "GitHub",
            "root_path": "/path/to/vault",
        }
        schema = IndexedObsidianVaultSchema(**valid_data)
        assert schema.id is None
        assert schema.files is None
        assert schema.indexed_at is None
        assert schema.file_count == 0
