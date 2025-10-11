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
    REMOTE: str = Field(
        default="remote",
        description="Scan for remote files using a remote file index.",
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
    parent_folder_markers: Optional[List[str]] = Field(
        default=None, description="List of parent folder markers to include."
    )


class ListBuilder:
    """Builds lists of files to process based on inclusion/exclusion criteria."""

    all_files: List[Path] = []
    filtered_files: List[Path] = []
    list_root: Optional[Path] = None
    options: ListBuilderOptions

    def __init__(self, options: ListBuilderOptions):
        self.options = options
        if self.options.mode == ListBuilderModes.FULL:
            self.list_root = Path.home()
        self.list_root = options.root_path.resolve() if options.root_path else None
        # Business logic to populate all_files
        if self.list_root and self.list_root.exists():
            if self.options.mode == ListBuilderModes.PROJECT:
                self.all_files = self.get_git_files()
            else:
                self.all_files = list(self.list_root.rglob("*"))
        else:
            print(Warning("Invalid or missing root path; no files to scan."))
            self.all_files = []

    def get_git_files(self) -> List[Path]:
        """Get list of files tracked by git in the repository."""
        import subprocess

        if not self.list_root or not (self.list_root / ".git").exists():
            print(Warning("Not a git repository; cannot get git files."))
            return []

        try:
            result = subprocess.run(
                ["git", "-C", str(self.list_root), "ls-files"],
                capture_output=True,
                text=True,
                check=True,
            )
            files = [
                self.list_root / f.strip()
                for f in result.stdout.splitlines()
                if f.strip()
            ]
            return files
        except subprocess.CalledProcessError as e:
            print(f"Error getting git files: {e}")
            return []
