"""
wembed_core/file_scanner/dot_scanignore.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Handles .scanignore files for excluding files during scanning.
"""

from fnmatch import fnmatch
from pathlib import Path

from pydantic import BaseModel, Field


class DotScanIgnoreFile(BaseModel):
    """Represents a .scanignore file and its patterns."""

    patterns: list[str] = []
    file_name = Field(default=".scanignore", frozen=True)

    @classmethod
    def load(cls, file_path: str | Path) -> "DotScanIgnoreFile":
        """Load patterns from a .scanignore file."""
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        if not file_path.is_file():
            raise FileNotFoundError(f"{file_path} does not exist or is not a file.")
        if not file_path.name == cls.file_name:
            raise ValueError(f"{file_path} is not a .scanignore file.")
        txt = file_path.read_text(encoding="utf-8")
        patterns = [line.strip() for line in txt.splitlines() if line.strip()]
        return cls(patterns=patterns)

    def apply_exclude_patterns(self, files: list[str] | list[Path]) -> list[str]:
        """Exclude files matching any of the patterns."""
        if not isinstance(files[0], str):
            files = [str(f.as_posix()) for f in files]
        excluded_files = set()
        for pattern in self.patterns:
            pattern_matches = {f for f in files if fnmatch(f, pattern)}
            excluded_files.update(pattern_matches)
        return [f for f in files if f not in excluded_files]

    def append_to_set(self, pattern_set: set[str]) -> None:
        """Append patterns to an existing set."""
        for pattern in self.patterns:
            pattern_set.add(pattern)

    def get_combined_set(self, file_set: set[str]) -> set[str]:
        """Return a new set combining existing set with patterns."""
        combined = file_set.copy()
        for pattern in self.patterns:
            combined.add(pattern)
        return combined

    @staticmethod
    def save(file_path: str, patterns: list[str]) -> None:
        """Save patterns to a .scanignore file."""
        with open(file_path, "w") as f:
            for pattern in patterns:
                f.write(f"{pattern}\n")

    @staticmethod
    def is_present(directory: Path) -> bool:
        """Check if a .scanignore file exists in the given directory."""
        return (directory / ".scanignore").is_file()
