"""
tests/test_controllers/test_indexing_controllers.py

Tests for the indexing-related controllers, ensuring database
functionalities for scan results, repos, vaults, and files.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from wembed_core.config import AppConfig
from wembed_core.controllers import IndexingResultsController
from wembed_core.database import DatabaseService
from wembed_core.schemas.indexing_result_schemas import IndexingResultSchema


class TestIndexingControllers:
    """Test suite for indexing-related controllers."""

    # region Fixtures
    @pytest.fixture
    def config(self) -> Mock:
        """Fixture for a mock AppConfig with an in-memory SQLite database."""
        config = Mock(spec=AppConfig)
        config.sqlalchemy_uri = "sqlite:///:memory:"
        config.debug = True
        config.host = "testhost"
        config.user = "testuser"
        return config

    @pytest.fixture
    def db_service(self, config: Mock) -> DatabaseService:
        """Fixture for an initialized DatabaseService."""
        service = DatabaseService(config)
        service.init_db()
        return service

    @pytest.fixture
    def scan_result_controller(
        self, db_service: DatabaseService
    ) -> IndexingResultsController:
        """Fixture to provide an instance of the ScanResultController."""
        return IndexingResultsController(db_service)

    # endregion

    def test_scan_result_controller_crud(
        self, scan_result_controller: IndexingResultsController, config: Mock
    ):
        """Tests basic create, get, and delete for ScanResultController."""
        # 1. Create a Scan Result
        scan_id = "test-scan-001"
        start_time = datetime.now(timezone.utc)
        scan_schema = IndexingResultSchema(
            id=scan_id,
            root_path="/path/to/scan",
            scan_name="Test Scan",
            scan_type="full",
            files=["/path/to/scan/file1.txt"],
            scan_start=start_time,
            scan_end=start_time + timedelta(seconds=30),
            duration=30.0,
            user=config.user,
            host=config.host,
        )

        created_scan = scan_result_controller.create(scan_schema)
        assert created_scan is not None
        assert created_scan.id == scan_id
        assert created_scan.scan_name == "Test Scan"

        # 2. Retrieve the Scan Result
        retrieved_scan = scan_result_controller.get_by_id(scan_id)
        assert retrieved_scan is not None
        assert retrieved_scan.id == created_scan.id
        assert retrieved_scan.user == config.user

        # 3. Retrieve all Scan Results (should be one)
        all_scans = scan_result_controller.get_all()
        assert len(all_scans) == 1
        assert all_scans[0].id == scan_id

        # 4. Delete the Scan Result
        delete_success = scan_result_controller.delete(scan_id)
        assert delete_success is True

        # 5. Verify it's gone
        assert scan_result_controller.get_by_id(scan_id) is None
        assert len(scan_result_controller.get_all()) == 0
