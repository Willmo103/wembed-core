import datetime
import json
import uuid

import pytest
from pydantic_core import ValidationError

from wembed_core.schemas.code_chunker import (
    CodeChunk,
    DependencyNode,
    FunctionCall,
    GitBranchSchema,
    GitCommitSchema,
    GitFileInfoSchema,
    ImportStatement,
    UsageNode,
)


@pytest.fixture
def sample_datetime():
    """Provides a consistent, timezone-aware datetime object for tests."""
    return datetime.datetime.now(datetime.timezone.utc)


@pytest.fixture
def git_commit_data(sample_datetime):
    return {
        "hash": "a1b2c3d4e5f6",
        "author": "Will Morris <willmorris103@gmail.com>",
        "date": sample_datetime,
        "message": "feat: Initial commit",
        "files_changed": ["src/main.py", "README.md"],
        "insertions": 150,
        "deletions": 10,
    }


@pytest.fixture
def git_file_info_data(sample_datetime):
    return {
        "file_path": "src/main.py",
        "last_commit_hash": "a1b2c3d4e5f6",
        "last_author": "Will Morris",
        "last_modified": sample_datetime,
        "total_commits": 5,
        "contributors": {"Will Morris", "Another Dev"},
        "lines_added_total": 200,
        "lines_removed_total": 50,
        "creation_date": sample_datetime - datetime.timedelta(days=10),
    }


@pytest.fixture
def code_chunk_data():
    return {
        "id": uuid.uuid4(),
        "content": "def hello():\n    print('Hello, World!')",
        "chunk_type": "function",
        "file_path": "src/main.py",
        "start_line": 10,
        "end_line": 11,
        "dependencies": set({"import os", "from utils import helper_function"}),
        "docstring": "A simple hello function.",
    }


# --- Test Classes ---


class TestGitCommitSchema:
    def test_successful_creation(self, git_commit_data):
        """Tests that a valid dictionary creates a GitCommitSchema instance."""
        commit = GitCommitSchema(**git_commit_data)
        assert commit.hash == git_commit_data["hash"]
        assert commit.author == git_commit_data["author"]

    def test_serialization(self, git_commit_data):
        """Tests that model_dump_json() works and datetimes are in ISO format."""
        commit = GitCommitSchema(**git_commit_data)
        commit_json = commit.model_dump_json()
        commit_dict = json.loads(commit_json)
        assert commit_dict["date"] == git_commit_data["date"].isoformat()

    def test_validation_error(self, git_commit_data):
        """Tests that incorrect data types raise a ValidationError."""
        git_commit_data["insertions"] = "one hundred"  # Invalid type
        with pytest.raises(ValidationError):
            GitCommitSchema(**git_commit_data)


class TestGitFileInfoSchema:
    def test_successful_creation(self, git_file_info_data):
        """Tests successful creation of GitFileInfoSchema."""
        info = GitFileInfoSchema(**git_file_info_data)
        assert info.file_path == git_file_info_data["file_path"]
        assert "Will Morris" in info.contributors

    def test_serialization(self, git_file_info_data):
        """Tests JSON serialization for GitFileInfoSchema."""
        info = GitFileInfoSchema(**git_file_info_data)
        info_json = info.model_dump_json()
        info_dict = json.loads(info_json)
        assert (
            info_dict["last_modified"]
            == git_file_info_data["last_modified"].isoformat()
        )


class TestCodeChunkSchema:
    def test_successful_creation(self, code_chunk_data):
        """Tests successful creation of CodeChunk."""
        chunk = CodeChunk(**code_chunk_data)
        assert chunk.chunk_type == "function"
        assert isinstance(chunk.id, uuid.UUID)

    def test_default_dependencies(self, code_chunk_data):
        """Tests that dependencies defaults to an empty set if not provided."""
        # Ensure dependencies is not in the input data
        code_chunk_data.pop("dependencies", None)
        chunk = CodeChunk(**code_chunk_data)
        assert chunk.dependencies == set()

    def test_serialization_with_uuid(self, code_chunk_data):
        """Tests that UUID is correctly serialized to a string."""
        chunk = CodeChunk(**code_chunk_data)
        chunk_json = chunk.model_dump_json()
        chunk_dict = json.loads(chunk_json)
        assert chunk_dict["id"] == str(code_chunk_data["id"])


@pytest.fixture
def sample_datetime():
    """Provides a consistent, timezone-aware datetime object for tests."""
    return datetime.datetime.now(datetime.timezone.utc)


@pytest.fixture
def git_commit_data(sample_datetime):
    return {
        "hash": "a1b2c3d4e5f6",
        "author": "Will Morris <willmorris103@gmail.com>",
        "date": sample_datetime,
        "message": "feat: Initial commit",
        "files_changed": ["src/main.py", "README.md"],
        "insertions": 150,
        "deletions": 10,
    }


@pytest.fixture
def git_file_info_data(sample_datetime):
    return {
        "file_path": "src/main.py",
        "last_commit_hash": "a1b2c3d4e5f6",
        "last_author": "Will Morris",
        "last_modified": sample_datetime,
        "total_commits": 5,
        "contributors": {"Will Morris", "Another Dev"},
        "lines_added_total": 200,
        "lines_removed_total": 50,
        "creation_date": sample_datetime - datetime.timedelta(days=10),
    }


@pytest.fixture
def git_branch_data(sample_datetime):
    return {
        "name": "main",
        "last_commit": "a1b2c3d4e5f6",
        "last_commit_date": sample_datetime,
        "is_current": True,
    }


@pytest.fixture
def dependency_node_data():
    return {
        "name": "requests",
        "version": "2.28.1",
        "source": "external",
        "used_by": {"src/api_client.py"},
        "imports": set(),
    }


@pytest.fixture
def import_statement_data():
    return {
        "module": "os",
        "names": ["path", "getenv"],
        "alias": None,
        "file_path": "src/utils.py",
        "line_number": 5,
        "is_from_import": True,
    }


@pytest.fixture
def code_chunk_data():
    return {
        "id": uuid.uuid4(),
        "content": "def hello():\n    print('Hello, World!')",
        "chunk_type": "function",
        "file_path": "src/main.py",
        "start_line": 10,
        "end_line": 11,
        "docstring": "A simple hello function.",
    }


@pytest.fixture
def usage_node_data():
    return {
        "identifier": "process_data",
        "file_path": "src/processing.py",
        "node_type": "function",
        "start_line": 25,
        "end_line": 50,
    }


@pytest.fixture
def function_call_data():
    return {
        "caller_file": "src/main.py",
        "caller_function": "main",
        "called_function": "process_data",
        "line_number": 15,
        "context": "process_data(user_input)",
    }


class TestGitCommitSchema:
    def test_successful_creation(self, git_commit_data):
        commit = GitCommitSchema(**git_commit_data)
        assert commit.hash == git_commit_data["hash"]

    def test_serialization(self, git_commit_data):
        commit = GitCommitSchema(**git_commit_data)
        commit_dict = json.loads(commit.model_dump_json())
        assert commit_dict["date"] == git_commit_data["date"].isoformat()

    def test_validation_error(self, git_commit_data):
        git_commit_data["insertions"] = "one hundred"
        with pytest.raises(ValidationError):
            GitCommitSchema(**git_commit_data)


class TestGitFileInfoSchema:
    def test_successful_creation(self, git_file_info_data):
        info = GitFileInfoSchema(**git_file_info_data)
        assert info.file_path == git_file_info_data["file_path"]

    def test_serialization(self, git_file_info_data):
        info = GitFileInfoSchema(**git_file_info_data)
        info_dict = json.loads(info.model_dump_json())
        assert (
            info_dict["last_modified"]
            == git_file_info_data["last_modified"].isoformat()
        )


class TestGitBranchSchema:
    def test_successful_creation(self, git_branch_data):
        branch = GitBranchSchema(**git_branch_data)
        assert branch.name == "main"
        assert branch.is_current is True

    def test_validation_error(self, git_branch_data):
        # FIX: Changed "yes" to a value that cannot be coerced to a bool
        git_branch_data["is_current"] = "not a bool"
        with pytest.raises(ValidationError):
            GitBranchSchema(**git_branch_data)


class TestDependencyNode:
    def test_successful_creation(self, dependency_node_data):
        node = DependencyNode(**dependency_node_data)
        assert node.name == "requests"
        assert node.is_used is False

    def test_default_values(self, dependency_node_data):
        dependency_node_data.pop("is_used", None)
        node = DependencyNode(**dependency_node_data)
        assert node.is_used is False


class TestImportStatement:
    def test_successful_creation(self, import_statement_data):
        imp = ImportStatement(**import_statement_data)
        assert imp.module == "os"
        assert "path" in imp.names


class TestCodeChunkSchema:
    def test_successful_creation(self, code_chunk_data):
        chunk = CodeChunk(**code_chunk_data)
        assert chunk.chunk_type == "function"

    def test_default_dependencies(self, code_chunk_data):
        code_chunk_data.pop("dependencies", None)
        chunk = CodeChunk(**code_chunk_data)
        assert chunk.dependencies == set()

    def test_serialization_with_uuid(self, code_chunk_data):
        chunk = CodeChunk(**code_chunk_data)
        chunk_dict = json.loads(chunk.model_dump_json())
        assert chunk_dict["id"] == str(code_chunk_data["id"])


class TestUsageNode:
    def test_successful_creation(self, usage_node_data):
        node = UsageNode(**usage_node_data)
        assert node.identifier == "process_data"

    def test_default_values(self, usage_node_data):
        usage_node_data.pop("is_entry_point", None)
        usage_node_data.pop("complexity_score", None)
        node = UsageNode(**usage_node_data)
        assert node.is_entry_point is False
        assert node.complexity_score == 0


class TestFunctionCall:
    def test_successful_creation(self, function_call_data):
        call = FunctionCall(**function_call_data)
        assert call.caller_function == "main"
        assert call.line_number == 15
