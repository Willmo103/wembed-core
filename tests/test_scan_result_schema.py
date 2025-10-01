"""
tests/test_scan_result_schema.py
Pytest tests for ScanResultSchema Pydantic model.
"""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from wembed_core.schemas.indexing_result_schemas import (
    IndexingResultList,
    IndexingResultSchema,
)


class TestScanResultsSchema:
    """Test suite for ScanResultSchema Pydantic model."""

    def test_valid_scan_result(self):
        """Test creating a valid ScanResultSchema instance."""
        scan_data = {
            "id": "scan123",
            "root_path": "/path/to/scan",
            "scan_type": "full",
            "scan_name": "Repo",
            "files": ["/path/to/scan/file1.txt", "/path/to/scan/file2.txt"],
            "scan_start": datetime.now(tz=timezone.utc),
            "scan_end": datetime.now(tz=timezone.utc) + timedelta(minutes=5),
            "duration": 300.0,
            "options": {"recursive": True, "follow_symlinks": False},
            "user": "testuser",
            "host": "testhost",
        }

        scan_result = IndexingResultSchema(**scan_data)

        assert scan_result.id == scan_data["id"]
        assert scan_result.root_path == scan_data["root_path"]
        assert scan_result.scan_type == scan_data["scan_type"]
        assert scan_result.scan_name == scan_data["scan_name"]
        assert scan_result.files == scan_data["files"]
        assert scan_result.scan_start == scan_data["scan_start"]
        assert scan_result.scan_end == scan_data["scan_end"]
        assert scan_result.duration == scan_data["duration"]
        assert scan_result.options == scan_data["options"]
        assert scan_result.user == scan_data["user"]
        assert scan_result.host == scan_data["host"]

    def test_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        incomplete_data = {
            # "id" is missing
            "root_path": "/path/to/scan",
            "scan_type": "full",
            "scan_start": datetime.now(tz=timezone.utc),
            "scan_end": None,
            "user": "testuser",
            "host": "testhost",
        }

        with pytest.raises(ValidationError) as exc_info:
            IndexingResultSchema(**incomplete_data)

        errors = exc_info.value.errors()
        assert any(error for error in errors)

    def test_invalid_field_type(self):
        """Test that invalid field types raise ValidationError."""
        invalid_data = {
            "id": 123,  # Should be str
            "root_path": "/path/to/scan",
            "scan_type": "full",
            "scan_start": "not-a-datetime",  # Should be datetime
            "user": "testuser",
            "host": "testhost",
        }
        with pytest.raises(ValidationError) as exc_info:
            IndexingResultSchema(**invalid_data)
        errors = exc_info.value.errors()
        assert any(error for error in errors)

    def test_optional_fields_with_none(self):
        """Test that optional fields can be omitted."""
        minimal_data = IndexingResultSchema(
            id="scan123",
            root_path="/path/to/scan",
            scan_name="Repo",
            scan_type="full",
            scan_start=datetime.now(tz=timezone.utc),
            scan_end=None,
            duration=None,
            options=None,
            user="testuser",
            host="testhost",
        ).model_dump()

        scan_result = IndexingResultSchema(**minimal_data)

        assert scan_result.id == minimal_data["id"]
        assert scan_result.root_path == minimal_data["root_path"]
        assert scan_result.scan_type == minimal_data["scan_type"]
        assert scan_result.scan_start == minimal_data["scan_start"]
        assert scan_result.user == minimal_data["user"]
        assert scan_result.host == minimal_data["host"]
        assert scan_result.files is None
        assert scan_result.scan_end is None
        assert scan_result.duration is None
        assert scan_result.options is None

    def test_total_files_computation(self):
        """Test the computed field total_files."""
        scan_data_with_files = {
            "id": "scan123",
            "root_path": "/path/to/scan",
            "scan_type": "full",
            "scan_name": "Repo",
            "files": ["/path/to/scan/file1.txt", "/path/to/scan/file2.txt"],
            "scan_start": datetime.now(tz=timezone.utc),
            "user": "testuser",
            "host": "testhost",
        }
        scan_result_with_files = IndexingResultSchema(**scan_data_with_files)
        assert scan_result_with_files.total_files == 2

        scan_data_no_files = {
            "id": "scan124",
            "root_path": "/path/to/scan",
            "scan_type": "incremental",
            "scan_name": "Repo Incremental",
            "files": None,
            "scan_start": datetime.now(tz=timezone.utc),
            "user": "testuser",
            "host": "testhost",
        }
        scan_result_no_files = IndexingResultSchema(**scan_data_no_files)
        assert scan_result_no_files.total_files == 0


class TestScanResultList:
    """Test suite for ScanResultList Pydantic model."""

    def test_add_and_iterate_results(self):
        """Test adding scan results and iterating over them."""
        scan_list = IndexingResultList(results=[])

        scan_data_1 = {
            "id": "scan1",
            "root_path": "/path/to/scan1",
            "scan_type": "full",
            "scan_name": "Scan 1",
            "files": ["/path/to/scan1/file1.txt"],
            "scan_start": datetime.now(timezone.utc) - timedelta(minutes=10),
            "scan_end": datetime.now(timezone.utc) - timedelta(minutes=5),
            "duration": 300.0,
            "options": {"recursive": True},
            "user": "user1",
            "host": "host1",
        }
        scan_data_2 = {
            "id": "scan2",
            "root_path": "/path/to/scan2",
            "scan_type": "incremental",
            "scan_name": "Scan 2",
            "files": ["/path/to/scan2/file2.txt"],
            "scan_start": datetime.now(timezone.utc) - timedelta(minutes=5),
            "scan_end": datetime.now(timezone.utc),
            "duration": 300.0,
            "options": {"recursive": False},
            "user": "user2",
            "host": "host2",
        }

        scan_result_1 = IndexingResultSchema(**scan_data_1)
        scan_result_2 = IndexingResultSchema(**scan_data_2)

        scan_list.add_result(scan_result_1)
        scan_list.add_result(scan_result_2)

        results = list(scan_list.iter_results())
        assert len(results) == 2
        assert results[0].id == "scan1"
        assert results[1].id == "scan2"

    def test_iterate_empty_list(self):
        """Test iterating over an empty ScanResultList."""
        scan_list = IndexingResultList(results=[])
        results = list(scan_list.iter_results())
        assert len(results) == 0

    def test_iter_results_generator(self):
        """Test that iter_results returns a generator."""
        scan_list = IndexingResultList(results=[])
        scan_data = {
            "id": "scan1",
            "root_path": "/path/to/scan1",
            "scan_type": "full",
            "scan_name": "Scan 1",
            "files": ["/path/to/scan1/file1.txt"],
            "scan_start": datetime.now(timezone.utc) - timedelta(minutes=10),
            "scan_end": datetime.now(timezone.utc) - timedelta(minutes=5),
            "duration": 300.0,
            "options": {"recursive": True},
            "user": "user1",
            "host": "host1",
        }
        scan_result = IndexingResultSchema(**scan_data)
        scan_list.add_result(scan_result)

        result_generator = scan_list.iter_results()
        assert hasattr(result_generator, "__iter__")
        assert not isinstance(result_generator, list)

        results = list(result_generator)
        assert len(results) == 1
        assert results[0].id == "scan1"

    def test_add_result(self):
        """Test that add_result correctly adds a ScanResultSchema to the list."""
        scan_list = IndexingResultList(results=[])
        scan_data = {
            "id": "scan1",
            "root_path": "/path/to/scan1",
            "scan_type": "full",
            "scan_name": "Scan 1",
            "files": ["/path/to/scan1/file1.txt"],
            "scan_start": datetime.now(timezone.utc) - timedelta(minutes=10),
            "scan_end": datetime.now(timezone.utc) - timedelta(minutes=5),
            "duration": 300.0,
            "options": {"recursive": True},
            "user": "user1",
            "host": "host1",
        }
        scan_result = IndexingResultSchema(**scan_data)
        scan_list.add_result(scan_result)

        assert len(scan_list.results) == 1
        assert scan_list.results[0].id == "scan1"
