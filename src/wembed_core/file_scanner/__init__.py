"""
File scanner package.
~~~~~~~~~~~~~~~~~~~~~~~
This package provides utilities and classes for scanning files, managing temporary repositories,
and building lists of files based on various criteria.
It includes functionality for handling .scanignore files, temporary git repository management,
and utility functions for file operations.
"""

from .dot_scanignore import DotScanIgnoreFile  # noqa: F401
from .list_builder import ListBuilder, ListBuilderOptions  # noqa: F401
from .tmp_repo_manager import TmpRepoManager  # noqa: F401
from .utils import (  # noqa: F401
    create_file_record_from_path,
    format_file_record_markdown,
    get_filelines_list_from_file_record,
)
