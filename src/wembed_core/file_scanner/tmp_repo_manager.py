"""
wembed_core/file_scanner/tmp_repo_manager.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Manages a temporary clone of a git repository for file scanning.
"""

import subprocess
from contextlib import contextmanager
from pathlib import Path


class TmpRepoManager:
    """
    Manages a temporary clone of a git repository for file scanning.
    Usage:
        with TmpRepoManager(repo_url, app_dir) as tmp_repo_path:
            # Use tmp_repo_path for file operations
            ...
            ...

    Attributes:
        - repo_url: URL of the git repository to clone.
        - tmp_dir: Path to the temporary directory.
        - keep: Whether to keep the temporary directory after use.

    """

    def __init__(self, repo_url: str, app_dir: Path, keep: bool = False):
        self.repo_url = repo_url
        self.tmp_dir = self._init_tmp_dir(app_dir)
        self.keep = keep

    def _init_tmp_dir(self, app_dir: Path) -> Path:
        """Initialize the temporary directory."""
        tmp_dir = app_dir / "tmp" / self._unique_id()
        if not tmp_dir.exists():
            tmp_dir.mkdir(parents=True)
        return tmp_dir

    def _unique_id(self) -> str:
        """Generate a unique identifier for the temporary repo."""
        import uuid

        return str(uuid.uuid4())[:8]

    @contextmanager
    def temp_repo(self):
        """Context manager to handle temporary repo setup and teardown."""
        if not self.tmp_dir.exists():
            self.tmp_dir.mkdir(parents=True)

        try:
            if self._pull_repo_to_tmp(self.repo_url, self.tmp_dir):
                yield self.tmp_dir
            else:
                raise RuntimeError("Failed to pull repository.")
        finally:
            if not self.keep:
                self._cleanup()

    def _pull_repo_to_tmp(self, repo_url: str, tmp_dir: Path) -> bool:
        """Clone or pull the repository into the temporary directory."""
        try:
            if not tmp_dir.exists():
                tmp_dir.mkdir(parents=True)
            if not (tmp_dir / ".git").exists():
                subprocess.run(["git", "clone", repo_url, str(tmp_dir)], check=True)
            else:
                subprocess.run(["git", "-C", str(tmp_dir), "pull"], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error pulling repository: {e}")
            return False

    def _cleanup(self):
        """Clean up the temporary directory."""
        if self.tmp_dir.exists():
            subprocess.run(["git", "-C", str(self.tmp_dir), "clean", "-fdx"])
            self.tmp_dir.rmdir()
