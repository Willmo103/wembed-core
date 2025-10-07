import datetime
import uuid
from typing import List, Optional, Set

from pydantic import BaseModel


class GitCommitSchema(BaseModel):
    """Represents a Git commit"""

    hash: str
    author: str
    date: datetime
    message: str
    files_changed: List[str]
    insertions: int
    deletions: int

    class Config:
        """Pydantic configuration to handle datetime serialization."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        from_attributes = True
        arbitrary_types_allowed = True


class GitFileInfoSchema(BaseModel):
    """Git information for a specific file"""

    file_path: str
    last_commit_hash: str
    last_author: str
    last_modified: datetime
    total_commits: int
    contributors: Set[str]
    lines_added_total: int
    lines_removed_total: int
    creation_date: datetime

    class Config:
        """Pydantic configuration to handle datetime serialization."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        from_attributes = True
        arbitrary_types_allowed = True


class GitBranchSchema(BaseModel):
    """Represents a Git branch"""

    name: str
    last_commit: str
    last_commit_date: datetime
    is_current: bool

    class Config:
        """Pydantic configuration to handle datetime serialization."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        from_attributes = True
        arbitrary_types_allowed = True


# In wembed_core/schemas/code_chunker.py


class DependencyNode(BaseModel):
    name: str
    version: Optional[str] = None
    source: str
    file_path: Optional[str] = None
    used_by: Set[str]
    imports: Set[str]
    is_used: bool = False

    class Config:
        from_attributes = True


class ImportStatement(BaseModel):
    """Represents an import statement"""

    module: str
    names: List[str]
    alias: Optional[str]
    file_path: str
    line_number: int
    is_from_import: bool

    class Config:
        """Pydantic configuration"""

        from_attributes = True


class CodeChunk(BaseModel):
    """Represents a chunk of code with metadata"""

    id: uuid.UUID
    content: str
    chunk_type: str  # 'function', 'class', 'method', 'import', 'module'
    file_path: str
    start_line: int
    end_line: int
    parent_id: Optional[str] = None
    dependencies: Set[str] = set()
    docstring: Optional[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = set()

    class Config:
        """Pydantic configuration"""

        arbitrary_types_allowed = True
        from_attributes = True


class UsageNode(BaseModel):
    """Node in the usage graph"""

    identifier: str  # function name, class name, etc.
    file_path: str
    node_type: str  # 'function', 'class', 'method', 'variable'
    start_line: int
    end_line: int
    is_entry_point: bool = False
    complexity_score: int = 0

    class Config:
        """Pydantic configuration"""

        arbitrary_types_allowed = True
        from_attributes = True


class FunctionCall(BaseModel):
    """Represents a function call in the code"""

    caller_file: str
    caller_function: str
    called_function: str
    line_number: int
    context: str

    class Config:
        """Pydantic configuration"""

        arbitrary_types_allowed = True
        from_attributes = True
