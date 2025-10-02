"""
tests/test_db_models/test_indexed_file_lines.py
Unit tests for the IndexedFileLines SQLAlchemy model.
"""

import pytest
from sqlalchemy import JSON, DateTime, Integer, String, Text

from wembed_core.models.indexed_file_lines import IndexedFileLines


class TestIndexedFileLines:
    """Unit tests for the IndexedFileLines model."""

    def test_table_name(self):
        """Test that the table name is correct."""
        assert IndexedFileLines.__tablename__ == "indexed_file_lines"

    def test_columns(self):
        """Test that all columns are defined correctly."""
        expected_columns = {
            "id",
            "file_id",
            "file_repo_name",
            "file_repo_type",
            "line_number",
            "line_text",
            "embedding",
            "created_at",
        }
        actual_columns = {
            col.name for col in IndexedFileLines.__table__.columns
        }  # noqa
        assert expected_columns == actual_columns

    def test_primary_key(self):
        """Test that the primary key is set correctly."""
        primary_keys = [
            col.name for col in IndexedFileLines.__table__.primary_key.columns
        ]
        assert primary_keys == ["id"]

    def test_foreign_key(self):
        """Test that the foreign key constraint is set correctly."""
        foreign_keys = list(IndexedFileLines.__table__.foreign_keys)  # noqa
        assert len(foreign_keys) == 1
        fk = foreign_keys[0]
        assert fk.parent.name == "file_id"
        assert str(fk.column) == "indexed_files.id"

    def test_column_types(self):
        """Test that column types are as expected."""
        column_types = {
            "id": Integer,
            "file_id": String,
            "file_repo_name": String,
            "file_repo_type": String,
            "line_number": Integer,
            "line_text": Text,
            "embedding": JSON,
            "created_at": DateTime,
        }
        for col_name, col_type in column_types.items():
            column = IndexedFileLines.__table__.columns[col_name]
            assert isinstance(column.type, col_type)

    def test_nullable_constraints(self):
        """Test that nullable constraints are set correctly."""
        nullable_constraints = {
            "id": False,
            "file_id": False,
            "file_repo_name": False,
            "file_repo_type": False,
            "line_number": False,
            "line_text": False,
            "embedding": True,
            "created_at": False,
        }
        for col_name, is_nullable in nullable_constraints.items():
            column = IndexedFileLines.__table__.columns[col_name]
            assert column.nullable == is_nullable
