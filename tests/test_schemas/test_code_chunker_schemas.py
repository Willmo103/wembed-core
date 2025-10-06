import datetime
import json
import uuid

import pytest
from pydantic_core import ValidationError

from wembed_core.schemas.code_chunker import (  # GitBranchSchema,; ImportStatement,; UsageNode,; FunctionCall,
    CodeChunk,
    GitCommitSchema,
    GitFileInfoSchema,
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
