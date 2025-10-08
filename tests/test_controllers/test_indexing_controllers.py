"""
tests/test_controllers/test_indexing_controllers.py

Tests for the indexing-related controllers, ensuring database
functionalities for scan results, repos, vaults, and files.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

from wembed_core.config import AppConfig
from wembed_core.controllers import (
    IndexedFileController,
    IndexedFileLineController,
    IndexedRepoController,
    IndexedVaultController,
    IndexingResultsController,
)
from wembed_core.database import DatabaseService
from wembed_core.schemas import (
    IndexedFileLineSchema,
    IndexedFileSchema,
    IndexedObsidianVaultSchema,
    IndexedRepoSchema,
    IndexingResultSchema,
)


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

    @pytest.fixture
    def indexed_repo_controller(
        self, db_service: DatabaseService
    ) -> IndexedRepoController:
        """Fixture to provide an instance of the IndexedRepoController."""
        return IndexedRepoController(db_service)

    @pytest.fixture
    def indexed_vault_controller(
        self, db_service: DatabaseService
    ) -> IndexedVaultController:
        """Fixture to provide an instance of the IndexedVaultController."""
        return IndexedVaultController(db_service)

    @pytest.fixture
    def indexed_file_controller(
        self, db_service: DatabaseService
    ) -> IndexedFileController:
        """Fixture to provide an instance of the IndexedFileController."""
        return IndexedFileController(db_service)

    @pytest.fixture
    def indexed_file_line_controller(
        self, db_service: DatabaseService
    ) -> IndexedFileLineController:
        """Fixture to provide an instance of the IndexedFileLineController."""
        return IndexedFileLineController(db_service)

    @pytest.fixture
    def sample_file_record(
        self, indexed_file_controller: IndexedFileController
    ) -> IndexedFileSchema:
        """Fixture that creates and returns a sample IndexedFiles ORM record."""
        now = datetime.now(timezone.utc)
        file_schema = IndexedFileSchema(
            id="test-file-for-lines",
            source_type="git",
            source_root="/path/to/repo",
            source_name="test-repo",
            path="/path/to/repo/main.py",
            sha256="a" * 64,
            created_at=now,
            updated_at=now,
            user="testuser",
            host="testhost",
            name="main.py",
            stem="main",
            relative_path="main.py",
            suffix=".py",
            md5="b" * 32,
            mode=644,
            size=1024,
            content=b"print('Hello, World!')",
            content_text="print('Hello, World!')",
            ctime_iso=now,
            mtime_iso=now,
            line_count=1,
            uri="file:///path/to/repo/main.py",
            mimetype="text/x-python",
            version=1,
        )
        return indexed_file_controller.create(file_schema)

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

    def test_indexed_repo_controller_crud(
        self, indexed_repo_controller: IndexedRepoController, config: Mock
    ):
        """Tests basic create, get, and delete for IndexedRepoController."""
        # 1. Create a Repo Record
        repo_name = "test-repo"
        repo_schema = IndexedRepoSchema(
            repo_name=repo_name,
            host=config.host,
            root_path="/path/to/repo",
            files=["file1.py", "file2.py"],
            file_count=2,
            indexed_at=datetime.now(timezone.utc),
        )
        created_repo = indexed_repo_controller.create(repo_schema)
        assert created_repo is not None
        assert created_repo.id is not None
        assert created_repo.repo_name == repo_name

        # 2. Retrieve by ID and Name
        retrieved_by_id = indexed_repo_controller.get_by_id(created_repo.id)
        retrieved_by_name = indexed_repo_controller.get_by_name(repo_name)
        assert retrieved_by_id is not None
        assert retrieved_by_name is not None
        assert retrieved_by_id.id == retrieved_by_name.id

        # 3. Get all repos
        all_repos = indexed_repo_controller.get_all()
        assert len(all_repos) == 1
        assert all_repos[0].id == created_repo.id

        # 4. Delete the repo
        delete_success = indexed_repo_controller.delete(created_repo.id)
        assert delete_success is True

        # 5. Verify it's gone
        assert indexed_repo_controller.get_by_id(created_repo.id) is None
        assert len(indexed_repo_controller.get_all()) == 0

    def test_indexed_vault_controller_crud(
        self, indexed_vault_controller: IndexedVaultController, config: Mock
    ):
        """Tests basic create, get, and delete for IndexedVaultController."""
        vault_name = "test-vault"
        vault_schema = IndexedObsidianVaultSchema(
            vault_name=vault_name, host=config.host, root_path="/path/to/vault"
        )
        created_vault = indexed_vault_controller.create(vault_schema)
        assert created_vault.vault_name == vault_name

        retrieved_by_id = indexed_vault_controller.get_by_id(created_vault.id)
        assert retrieved_by_id is not None and retrieved_by_id.id == created_vault.id

        assert len(indexed_vault_controller.get_all()) == 1
        assert indexed_vault_controller.delete(created_vault.id) is True
        assert indexed_vault_controller.get_by_id(created_vault.id) is None

    def test_indexed_file_controller_crud(
        self, indexed_file_controller: IndexedFileController
    ):
        """Tests basic create, get, and delete for IndexedFileController."""
        now = datetime.now(timezone.utc)
        file_id = "test-file-001"
        file_schema = IndexedFileSchema(
            id="test-file-001",
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
        created_file = indexed_file_controller.create(file_schema)
        assert created_file.id == file_id

        retrieved_file = indexed_file_controller.get_by_id(file_id)
        assert retrieved_file is not None and retrieved_file.id == file_id

        assert indexed_file_controller.delete(file_id) is True
        assert indexed_file_controller.get_by_id(file_id) is None

    def test_indexed_file_line_controller_crud(
        self,
        indexed_file_line_controller: IndexedFileLineController,
        sample_file_record,  # Uses fixture to ensure a parent file exists
    ):
        """Tests create, get, update, and delete for IndexedFileLineController."""
        # 1. Batch create lines linked to the sample_file_record
        line_schemas = [
            IndexedFileLineSchema(
                file_id=sample_file_record.id,
                file_source_name=sample_file_record.source_name,
                file_source_type=sample_file_record.source_type,
                line_number=i,
                line_text=f"Line {i}",
            )
            for i in range(3)
        ]
        created_lines = indexed_file_line_controller.create_batch(line_schemas)
        assert len(created_lines) == 3

        # 2. Retrieve the lines by file_id
        retrieved_lines = indexed_file_line_controller.get_by_file_id(
            sample_file_record.id
        )
        assert len(retrieved_lines) == 3
        assert retrieved_lines[1].line_text == "Line 1"

        # 3. Update the embedding for one line
        line_to_update = retrieved_lines[0]
        new_embedding = [0.1, 0.2, 0.3]
        updated_line = indexed_file_line_controller.update_embedding(
            line_to_update.id, new_embedding
        )
        assert updated_line.embedding == new_embedding

        # 4. Delete all lines by file_id
        deleted_count = indexed_file_line_controller.delete_by_file_id(
            sample_file_record.id
        )
        assert deleted_count == 3

        # 5. Verify they are gone
        final_lines = indexed_file_line_controller.get_by_file_id(sample_file_record.id)
        assert len(final_lines) == 0
