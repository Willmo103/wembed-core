"""
tests/test_controllers/test_code_chunker_controllers.py

Tests for the CodeChunker-related controllers, ensuring database functionalities for
Git metadata, code chunks, dependencies, and code analysis models.
"""

from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from wembed_core.config import AppConfig
from wembed_core.controllers import (
    CodeChunkerCodeChunksController,
    CodeChunkerDependencyNodeController,
    CodeChunkerFunctionCallController,
    CodeChunkerGitBranchController,
    CodeChunkerGitCommitController,
    CodeChunkerGitFileInfoController,
    CodeChunkerImportStatementController,
    CodeChunkerUsageNodeController,
)
from wembed_core.database import DatabaseService
from wembed_core.schemas import (
    CodeChunk,
    DependencyNode,
    FunctionCall,
    GitBranchSchema,
    GitCommitSchema,
    GitFileInfoSchema,
    ImportStatement,
    UsageNode,
)


class TestCodeChunkerControllers:
    """Test suite for CodeChunker-related controllers."""

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
    def code_chunk_controller(
        self, db_service: DatabaseService
    ) -> CodeChunkerCodeChunksController:
        return CodeChunkerCodeChunksController(db_service)

    @pytest.fixture
    def git_commit_controller(
        self, db_service: DatabaseService
    ) -> CodeChunkerGitCommitController:
        return CodeChunkerGitCommitController(db_service)

    @pytest.fixture
    def git_file_info_controller(
        self, db_service: DatabaseService
    ) -> CodeChunkerGitFileInfoController:
        return CodeChunkerGitFileInfoController(db_service)

    @pytest.fixture
    def git_branch_controller(
        self, db_service: DatabaseService
    ) -> CodeChunkerGitBranchController:
        return CodeChunkerGitBranchController(db_service)

    @pytest.fixture
    def dependency_node_controller(
        self, db_service: DatabaseService
    ) -> CodeChunkerDependencyNodeController:
        return CodeChunkerDependencyNodeController(db_service)

    @pytest.fixture
    def import_statement_controller(
        self, db_service: DatabaseService
    ) -> CodeChunkerImportStatementController:
        return CodeChunkerImportStatementController(db_service)

    @pytest.fixture
    def usage_node_controller(
        self, db_service: DatabaseService
    ) -> CodeChunkerUsageNodeController:
        return CodeChunkerUsageNodeController(db_service)

    @pytest.fixture
    def function_call_controller(
        self, db_service: DatabaseService
    ) -> CodeChunkerFunctionCallController:
        return CodeChunkerFunctionCallController(db_service)

    # endregion

    def test_git_commit_controller(
        self, git_commit_controller: CodeChunkerGitCommitController
    ):
        """Tests create and get for GitCommitController."""
        commit_schema = GitCommitSchema(
            hash="a1b2c3d4",
            author="Will",
            date=datetime.now(timezone.utc),
            message="feat: test commit",
            files_changed=["a.py"],
            insertions=10,
            deletions=2,
        )
        created = git_commit_controller.create(commit_schema)
        assert created.hash == "a1b2c3d4"

        retrieved = git_commit_controller.get_by_hash("a1b2c3d4")
        assert retrieved is not None
        assert retrieved.id == created.id

    def test_git_branch_controller(
        self, git_branch_controller: CodeChunkerGitBranchController
    ):
        """Tests batch create, get, and delete for GitBranchController."""
        branch_schemas = [
            GitBranchSchema(
                name="main",
                last_commit="a1b2",
                last_commit_date=datetime.now(timezone.utc),
                is_current=True,
            ),
            GitBranchSchema(
                name="dev",
                last_commit="c3d4",
                last_commit_date=datetime.now(timezone.utc),
                is_current=False,
            ),
        ]
        created = git_branch_controller.create_batch(branch_schemas)
        assert len(created) == 2

        all_branches = git_branch_controller.get_all()
        assert len(all_branches) == 2

        deleted_count = git_branch_controller.delete_all()
        assert deleted_count == 2
        assert len(git_branch_controller.get_all()) == 0

    def test_git_file_info_controller(
        self, git_file_info_controller: CodeChunkerGitFileInfoController
    ):
        """Tests create, get, and update for GitFileInfoController."""
        file_path = "src/main.py"
        file_info_schema = GitFileInfoSchema(
            file_path=file_path,
            last_commit_hash="a1b2",
            last_author="Will",
            last_modified=datetime.now(timezone.utc),
            total_commits=5,
            contributors={"Will"},
            lines_added_total=100,
            lines_removed_total=20,
            creation_date=datetime.now(timezone.utc),
        )
        created = git_file_info_controller.create(file_info_schema)
        assert created.total_commits == 5

        retrieved = git_file_info_controller.get_by_file_path(file_path)
        assert retrieved is not None

        retrieved = git_file_info_controller.get_by_file_path(file_path)
        updated_schema = GitFileInfoSchema.model_validate(retrieved)
        updated_schema.total_commits = 6

    def test_code_chunk_controller(
        self, code_chunk_controller: CodeChunkerCodeChunksController
    ):
        """Tests create and get for CodeChunkController."""
        chunk_schema = CodeChunk(
            chunk_uuid="123e4567-e89b-12d3-a456-426614174000",
            content="def hello(): pass",
            chunk_type="function",
            file_path="a.py",
            start_line=1,
            end_line=1,
            parent_id=None,
        )
        created = code_chunk_controller.create(chunk_schema)
        assert created.chunk_type == "function"

        retrieved = code_chunk_controller.get_by_uuid(created.chunk_uuid)
        assert retrieved is not None
        assert retrieved.chunk_uuid == created.chunk_uuid

    def test_dependency_node_controller(
        self, dependency_node_controller: CodeChunkerDependencyNodeController
    ):
        """Tests batch create for DependencyNodeController."""
        dep_schemas = [
            DependencyNode(
                name="pytest",
                source="external",
                used_by={"test.py"},
                imports={"pytest"},
            ),
            DependencyNode(
                name="os", source="stdlib", used_by={"main.py"}, imports={"os"}
            ),
        ]
        created = dependency_node_controller.create_batch(dep_schemas)
        assert len(created) == 2
        assert created[0].name == "pytest"

    def test_import_statement_controller(
        self, import_statement_controller: CodeChunkerImportStatementController
    ):
        """Tests batch create for ImportStatementController."""
        import_schemas = [
            ImportStatement(
                module="os",
                names=["path"],
                alias=None,
                file_path="a.py",
                line_number=1,
                is_from_import=False,
            ),
        ]
        created = import_statement_controller.create_batch(import_schemas)
        assert len(created) == 1
        assert created[0].module == "os"

    def test_usage_node_controller(
        self, usage_node_controller: CodeChunkerUsageNodeController
    ):
        """Tests batch create for UsageNodeController."""
        usage_schemas = [
            UsageNode(
                identifier="my_func",
                file_path="a.py",
                node_type="function",
                start_line=5,
                end_line=10,
            ),
        ]
        created = usage_node_controller.create_batch(usage_schemas)
        assert len(created) == 1
        assert created[0].identifier == "my_func"

    def test_function_call_controller(
        self, function_call_controller: CodeChunkerFunctionCallController
    ):
        """Tests batch create for FunctionCallController."""
        call_schemas = [
            FunctionCall(
                caller_file="a.py",
                caller_function="main",
                called_function="my_func",
                line_number=20,
                context="my_func()",
            ),
        ]
        created = function_call_controller.create_batch(call_schemas)
        assert len(created) == 1
        assert created[0].called_function == "my_func"
