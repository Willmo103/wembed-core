from pathlib import Path
from typing import List, Optional, Set

from pydantic import BaseModel, Field

from wembed_core.constants import IGNORE_EXTENSIONS, IGNORE_PARTS


class ListBuilderOptions(BaseModel):
    root_path: Optional[Path] = Field(
        default=Path.cwd(), description="Root directory to start scanning from."
    )
    match_patterns: Optional[List[str]] = Field(
        default=None, description="List of glob patterns to match files."
    )
    patterns: Optional[List[str]] = Field(
        default=None, description="List of glob patterns to match files."
    )
    exclude_ext: Optional[Set[str]] = Field(
        default=IGNORE_EXTENSIONS, description="Set of file extensions to exclude."
    )
    exclude_parts: Optional[Set[str]] = Field(
        default=IGNORE_PARTS, description="Set of path segments to exclude."
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
