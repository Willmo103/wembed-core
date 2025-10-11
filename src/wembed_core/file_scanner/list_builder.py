from enum import Enum
from pathlib import Path
from typing import List, Optional, Set

from pydantic import BaseModel, Field, computed_field

from wembed_core.constants import (
    IGNORE_EXTENSIONS,
    IGNORE_PARTS,
    OBSIDIAN_MARKER,
    REPO_MARKER,
)


class ListBuilderModes(str, Enum):
    """Defines modes for ListBuilder operation."""

    FULL: str = Field(
        default="full",
        description="Full scan of the filesystem for all markers."
        " Uses all configured roots in the ~/wembed/config.json:scan_root_paths section.",
        frozen=True,
    )
    REPOSITORY: str = Field(
        default="repo",
        description="Scan for multiple repository folders for repository indexing.",
        frozen=True,
    )
    OBSIDIAN: str = Field(
        default="obsidian",
        description="Scan for multiple Obsidian vault folders for Obsidian indexing.",
        frozen=True,
    )
    PROJECT: str = Field(
        default="project",
        description="Scan inside of a project folder using git ls-files to find files as the default ignoring configuration.",
        frozen=True,
    )


class ListBuilderOptions(BaseModel):
    """
    ListBuilderOptions defines configuration options for building a list of files
    to be processed. It includes parameters for scanning mode, root path, file
    matching patterns, subdirectory filtering, ignored extensions and path parts,
    recursion, and parent folder markers.

    Attributes:
        mode (str): Mode of operation
        root_path (Optional[Path]): Root directory to start scanning from.
        match_patterns (Optional[List[str]]): List of glob patterns to match files.
        subdirs (Optional[List[str]]): List of subdirectories to limit results to.
        ignored_extensions (Optional[Set[str]]): Set of file extensions to exclude.
        ignored_file_parts (Optional[Set[str]]): Set of path segments to exclude.
        recursive (Optional[bool]): Whether to scan directories recursively.
        parent_folder_markers (Optional[List[str]]): List of parent folder markers to include.
    """

    mode: str = Field(
        default=None,
        description="Mode of operation: 'git' for git-tracked files, 'fs' for filesystem scan.",
    )
    root_path: Optional[Path] = Field(
        default=Path.cwd(), description="Root directory to start scanning from."
    )
    match_patterns: Optional[List[str]] = Field(
        default=None, description="List of glob patterns to match files."
    )
    subdirs: Optional[List[str]] = Field(
        default=None, description="List of subdirectories to limit results to."
    )
    ignored_extensions: Optional[Set[str]] = Field(
        default=IGNORE_EXTENSIONS, description="Set of file extensions to exclude."
    )
    ignored_file_parts: Optional[Set[str]] = Field(
        default=IGNORE_PARTS, description="Set of path segments to exclude."
    )
    recursive: Optional[bool] = Field(
        default=True, description="Whether to scan directories recursively."
    )
    parent_folder_markers: Optional[List[str]] = Field(
        default=None, description="List of parent folder markers to include."
    )


class ListBuilder:
    """Builds lists of files to process based on inclusion/exclusion criteria."""

    def __init__(
        self,
        root_path: Optional[Path] = Path.cwd(),
        match_patterns: Optional[list[str]] = None,
        exclude_ext: Optional[Set[str]] = None,
        exclude_parts: Optional[Set[str]] = None,
    ):
        self.all_files = []
        self.match_patterns = match_patterns or []
        self.exclude_ext = exclude_ext or IGNORE_EXTENSIONS
        self.exclude_parts = exclude_parts or IGNORE_PARTS
