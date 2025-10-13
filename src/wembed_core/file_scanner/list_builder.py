import fnmatch
from enum import Enum
from pathlib import Path
from sys import prefix
from typing import List, Optional, Set

from pydantic import BaseModel, Field, computed_field

from wembed_core.constants import (
    IGNORE_EXTENSIONS,
    IGNORE_PARTS,
    OBSIDIAN_MARKER,
    REPO_MARKER,
)

from .dot_scanignore import DotScanIgnoreFile


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

    all_files: Optional[List[Path]] = Field(
        default=None, description="All possible files found depending on mode."
    )
    filtered_files: Optional[List[Path]] = Field(
        default=None, description="Files filtered by inclusion/exclusion criteria."
    )
    mode: Optional[ListBuilderModes] = Field(
        default=None, description="Mode of operation."
    )
    root: Optional[Path] = Field(
        default=None, description="Root directory for scanning."
    )
    options: ListBuilderOptions
    marked_dirs: Optional[Set[Path]] = None

    def __init__(self, options: ListBuilderOptions):

        self.options = options
        self.mode = ListBuilderModes(options.mode) if options.mode else None
        self.root = options.root_path.resolve() if options.root_path else None
        if self.mode == ListBuilderModes.FULL:
            self.root = Path.home()
        elif self.mode == ListBuilderModes.PROJECT:
            self.root = options.root_path.resolve() if options.root_path else None
            self.all_files = self.get_git_files()
        self.root = options.root_path.resolve() if options.root_path else None
        # Business logic to populate all_files
        if not (self.root and self.root.exists()):
            raise ValueError("Invalid or missing root path; cannot scan files.")

    def get_git_files(self) -> Optional[List[Path]]:
        """Get list of files tracked by git in the repository."""
        import subprocess

        if not self.root or not (self.root / ".git").exists():
            print(Warning("Not a git repository; cannot get git files."))
            return []

        try:
            result = subprocess.run(
                ["git", "-C", str(self.root), "ls-files"],
                capture_output=True,
                text=True,
                check=True,
            )
            files = [
                self.root / f.strip() for f in result.stdout.splitlines() if f.strip()
            ]
            return files
        except subprocess.CalledProcessError as e:
            print(f"Error getting git files: {e}")
            return []

    def process_paths_for_subdirs(
        self,
    ) -> tuple[List[str], List[str]]:
        """Process the list of files to filter and adjust paths based on specified subdirectories.
        If subdirs are specified, this method filters the files to include only those
        that reside within the given subdirectories. It then adjusts the paths to be
        relative to the subdirectory.

        Returns:
            A tuple containing:
            - original_paths: Filtered list of original paths (e.g., ['src/app/main.py']).
            - adjusted_paths: Paths adjusted to be relative to the sub_dir (e.g., ['main.py']).
        """
        if not self.options.subdirs:
            return self.filtered_files, self.filtered_files

        # Normalize the path to use forward slashes and remove any leading/trailing ones.
        normalized_dirs = [
            sub_dir.strip("/\\").replace("\\", "/") for sub_dir in self.options.subdirs
        ]
        if not any(normalized_dirs):
            return self.filtered_files, self.filtered_files

        prefixes = [nd + "/" for nd in normalized_dirs]

        # Find all files that start with the subdirectory path.
        original_paths = [
            f for f in self.files if any(f.startswith(prefix) for prefix in prefixes)
        ]

        # Create new paths with the subdirectory prefix removed.
        adjusted_paths = [f.removeprefix(prefix) for f in original_paths]

        return original_paths, adjusted_paths

    def path_has_ignored_part(self, item: Path) -> bool:
        """
        Checks each pathlib.Path().part of `item` against each str in `parts`
        and returns True if any match. The default for 'parts' comes from
        [src/wembed/config/ignore_parts.py] if the
        IGNORE_PARTS environment variable is not set.

        Args:
            item (pathlib.Path): The file or directory path to check.
            parts (Set[str]): A set of path segments to ignore.

        Returns:
            bool: True if any part of the path matches an ignored segment, False otherwise.
        """
        if DotScanIgnoreFile.is_present(item.parent):
            scanignore = self.try_load_scanignore(item.parent)
            if scanignore:
                if scanignore.apply_exclude_patterns([item]):
                    return True
        return any(seg in self.options.ignored_file_parts for seg in item.parts)

    def path_has_ignored_extension(self, item: Path) -> bool:
        """
        Checks the suffix of `item` against each str in `extensions`
        and returns True if any match. The default for 'extensions' comes from
        [src/wembed/config/ignore_extensions.py] if the
        IGNORE_EXTENSIONS environment variable is not set.

        Args:
            item (pathlib.Path): The file or directory path to check.
            extensions (Set[str]): A set of file extensions to ignore.
        Returns:
            bool: True if the file's extension matches an ignored extension, False otherwise.
        """
        if DotScanIgnoreFile.is_present(item.parent):
            scanignore = self.try_load_scanignore(item.parent)
            if scanignore:
                if scanignore.apply_exclude_patterns([item]):
                    return True
        return item.suffix in self.options.ignored_extensions

    def try_load_scanignore(
        self, target_directory: Optional[Path]
    ) -> Optional[DotScanIgnoreFile]:
        """Attempts to load a .scanignore file from the base directory."""
        if not target_directory:
            return None

        scanignore_path = target_directory / ".scanignore"
        if scanignore_path.exists():
            try:
                return DotScanIgnoreFile.load(scanignore_path)
            except Exception as e:
                print(f"Error loading .scanignore: {e}")
                return None
        return None

    def try_load_docs_folder_and_readmes_only(
        self, target_directory: Optional[Path]
    ) -> Optional[Set[Path]]:
        """ """
        targets = set(
            "docs",
            "examples",
            "*README*",
            "*readme*",
            "*.md",
            "*MD",
            "*.txt",
            "*.rst",
            "*.RST",
            "*.adoc",
            "*.ADOC",
            "*.asciidoc",
            "*.ASCIIDOC",
            "*.org",
            "*.ORG",
            "*.wiki",
            "*.WIKI",
            "*.markdown",
            "*.MARKDOWN",
            "*.mdown",
            "*.MDOWN",
            "*.mkd",
            "*.MKD",
            "*.mkdn",
            "*.MKDN",
            "*.mdx",
            "*.MDX",
            "*.METADATA",
            "*.metadata",
        )
        if not self.all_files:
            self.all_files = target_directory.rglob("*")
        marked_dirs = set()
        for file in self.all_files:
            if file.is_dir() and any(
                fnmatch(file.name, pattern) for pattern in targets
            ):
                marked_dirs.add(file.resolve())
        return marked_dirs if marked_dirs else None

    def try_locate_obsidian_vaults(
        self, target_directory: Optional[Path]
    ) -> Optional[Set[Path]]:
        """Returns a set of the root folders containing a `.obsidian` folder."""
        if not target_directory:
            return None
        if not self.all_files:
            self.all_files = target_directory.rglob("*")
        vault_dirs = set()
        for file in self.all_files:
            if file.is_dir() and file.name == OBSIDIAN_MARKER:
                vault_dirs.add(file.parent.resolve())
        return vault_dirs if vault_dirs else None

    def try_locate_repositories(
        self, target_directory: Optional[Path]
    ) -> Optional[Set[Path]]:
        """Returns a set of the root folders containing a `.git` folder."""
        if not target_directory:
            return None
        if not self.all_files:
            self.all_files = target_directory.rglob("*")
        repo_dirs = set()
        for file in self.all_files:
            if file.is_dir() and file.name == REPO_MARKER:
                repo_dirs.add(file.parent.resolve())
        return repo_dirs if repo_dirs else None

    def try_locate_images(
        self, target_directory: Optional[Path]
    ) -> Optional[Set[Path]]:
        """Returns a set of image file paths."""
        if not target_directory:
            return None
        if not self.all_files:
            self.all_files = target_directory.rglob("*")
        image_files = set()
        image_extensions = {
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".tiff",
            ".svg",
            ".webp",
            ".nef",
            ".cr2",
            ".arw",
            ".orf",
            ".rw2",
        }
        for file in self.all_files:
            if file.is_file() and file.suffix.lower() in image_extensions:
                image_files.add(file.resolve())
        return image_files if image_files else None

    def try_locate_dL_ingestiable_files(
        self, target_directory: Optional[Path]
    ) -> Optional[Set[Path]]:
        """Returns a set of the root folders containing dL ingestiable files."""
        if not target_directory:
            return None
        if not self.all_files:
            self.all_files = target_directory.rglob("*")
        dl_input_dirs = set()
        dl_input_extensions = {
            ".pdf",
            ".docx",
            ".pptx",
            ".xlsx",
            ".html",
            ".xhtml",
            ".wav",
            ".mp3",
            ".vtt",
            ".csv",
            ".png",
            ".tiff",
            ".jpeg",
            ".webp",
            ".bmp",
            ".jpeg",
        }
        for file in self.all_files:
            if file.is_file() and file.suffix.lower() in dl_input_extensions:
                dl_input_dirs.add(file.parent.resolve())
        return dl_input_dirs if dl_input_dirs else None
