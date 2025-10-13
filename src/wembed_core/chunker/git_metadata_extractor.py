"""
wembed_core/chunker/git_metadata_extractor.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Extracts Git metadata for files and repositories.
This module provides the GitMetadataExtractor class which interfaces with the Git command line
to retrieve information such as commit history, authorship, branches, and file-specific metadata.
"""

import os
import re
import subprocess
from datetime import datetime
from typing import Dict, List, Optional

from typer import echo

from wembed_core.schemas import (
    GitBranchSchema,
    GitCommitSchema,
    GitFileInfoSchema,
)


class GitMetadataExtractor:
    """Extracts Git metadata for files and repositories"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = os.path.abspath(repo_path)
        self.git_dir = os.path.join(self.repo_path, ".git")

        if not os.path.exists(self.git_dir):
            raise ValueError(f"Not a git repository: {self.repo_path}")

    def _run_git_command(self, command: List[str]) -> str:
        """Run a git command and return the output"""
        try:
            result = subprocess.run(
                ["git"] + command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {' '.join(command)}")
            print(f"Error: {e.stderr}")
            return ""

    def get_file_info(self, file_path: str) -> Optional[GitFileInfoSchema]:
        """Get Git metadata for a specific file"""
        rel_path = os.path.relpath(file_path, self.repo_path)

        # Check if file is tracked by git
        tracked_files = self._run_git_command(["ls-files"]).split("\n")
        if rel_path not in tracked_files:
            return None

        # Get last commit info for file
        last_commit_info = self._run_git_command(
            ["log", "-1", "--format=%H|%an|%ad", "--date=iso", "--", rel_path]
        )

        if not last_commit_info:
            return None

        hash_part, author, date_str = last_commit_info.split("|", 2)
        last_modified = datetime.fromisoformat(date_str.replace(" ", "T"))

        # Get total commits for file
        commit_count = self._run_git_command(
            ["rev-list", "--count", "HEAD", "--", rel_path]
        )
        total_commits = int(commit_count) if commit_count.isdigit() else 0

        # Get all contributors
        contributors_output = self._run_git_command(
            ["log", "--format=%an", "--", rel_path]
        )
        contributors = (
            set(contributors_output.split("\n")) if contributors_output else set()
        )

        # Get file creation date (first commit)
        creation_info = self._run_git_command(
            ["log", "--format=%ad", "--date=iso", "--reverse", "--", rel_path]
        )
        creation_date = last_modified  # fallback
        if creation_info:
            first_date = creation_info.split("\n")[0]
            creation_date = datetime.fromisoformat(first_date.replace(" ", "T"))

        # Get line statistics
        stats = self._run_git_command(
            ["log", "--numstat", "--pretty=format:", "--", rel_path]
        )

        lines_added_total = 0
        lines_removed_total = 0

        for line in stats.split("\n"):
            if line.strip() and "\t" in line:
                parts = line.split("\t")
                if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
                    lines_added_total += int(parts[0])
                    lines_removed_total += int(parts[1])

        return GitFileInfoSchema(
            file_path=file_path,
            last_commit_hash=hash_part,
            last_author=author,
            last_modified=last_modified,
            total_commits=total_commits,
            contributors=contributors,
            lines_added_total=lines_added_total,
            lines_removed_total=lines_removed_total,
            creation_date=creation_date,
        )

    def get_recent_commits(
        self, limit: int = 50, file_path: Optional[str] = None
    ) -> List[GitCommitSchema]:
        """Get recent commits, optionally filtered by file"""
        cmd = [
            "log",
            f"--max-count={limit}",
            "--format=%H|%an|%ad|%s",
            "--date=iso",
        ]
        if file_path:
            cmd.extend(["--", os.path.relpath(file_path, self.repo_path)])

        output = self._run_git_command(cmd)
        commits = []

        for line in output.split("\n"):
            if not line.strip():
                continue

            parts = line.split("|", 3)
            if len(parts) >= 4:
                hash_part, author, date_str, message = parts
                commit_date = datetime.fromisoformat(date_str.replace(" ", "T"))

                # Get files changed in this commit
                files_changed = self._run_git_command(
                    [
                        "diff-tree",
                        "--no-commit-id",
                        "--name-only",
                        "-r",
                        hash_part,
                    ]
                ).split("\n")
                files_changed = [f for f in files_changed if f.strip()]

                # Get insertion/deletion stats
                stats = self._run_git_command(
                    ["show", "--stat", "--format=", hash_part]
                )

                insertions, deletions = self._parse_commit_stats(stats)

                commits.append(
                    GitCommitSchema(
                        hash=hash_part,
                        author=author,
                        date=commit_date,
                        message=message,
                        files_changed=files_changed,
                        insertions=insertions,
                        deletions=deletions,
                    )
                )

        return commits

    def _parse_commit_stats(self, stats: str) -> tuple[int, int]:
        """Parse git show --stat output to get insertions/deletions"""
        insertions = 0
        deletions = 0

        # Look for pattern like "5 files changed, 42 insertions(+), 13 deletions(-)"
        matches = re.findall(r"(\d+) insertion[s]?\(\+\)", stats)
        if matches:
            insertions = int(matches[0])

        matches = re.findall(r"(\d+) deletion[s]?\(\-\)", stats)
        if matches:
            deletions = int(matches[0])

        return insertions, deletions

    def get_branches(self) -> List[GitBranchSchema]:
        """Get all branches in the repository"""
        branches_output = self._run_git_command(
            [
                "branch",
                "-v",
                "--format=%(refname:short)|%(objectname)|%(committerdate:iso)|%(HEAD)",
            ]
        )
        current_branch = self._run_git_command(["branch", "--show-current"])

        branches = []
        for line in branches_output.split("\n"):
            if not line.strip():
                continue

            if "|" in line:
                parts = line.split("|")
                if len(parts) >= 3:
                    name, commit_hash, date_str = parts[0], parts[1], parts[2]
                    is_current = name == current_branch

                    try:
                        commit_date = datetime.fromisoformat(date_str.replace(" ", "T"))
                    except Exception as e:
                        echo(f"Error parsing date '{date_str}': {e}", err=True)
                        commit_date = datetime.now()

                    branches.append(
                        GitBranchSchema(
                            name=name,
                            last_commit=commit_hash,
                            last_commit_date=commit_date,
                            is_current=is_current,
                        )
                    )

        return branches

    def get_repository_stats(self) -> Dict:
        """Get overall repository statistics"""
        total_commits = self._run_git_command(["rev-list", "--count", "HEAD"])
        total_authors = self._run_git_command(["shortlog", "-sn", "--all"])

        author_count = len([line for line in total_authors.split("\n") if line.strip()])

        # Get repository age
        first_commit = self._run_git_command(
            ["log", "--reverse", "--format=%ad", "--date=iso", "-1"]
        )
        last_commit = self._run_git_command(["log", "--format=%ad", "--date=iso", "-1"])

        repo_age_days = 0
        if first_commit and last_commit:
            try:
                first_date = datetime.fromisoformat(first_commit.replace(" ", "T"))
                last_date = datetime.fromisoformat(last_commit.replace(" ", "T"))
                repo_age_days = (last_date - first_date).days
            except Exception as e:
                echo(f"Error parsing dates: {e}", err=True)
                pass

        return {
            "total_commits": (int(total_commits) if total_commits.isdigit() else 0),
            "total_authors": author_count,
            "repository_age_days": repo_age_days,
            "current_branch": self._run_git_command(["branch", "--show-current"]),
            "remote_url": self._run_git_command(
                ["config", "--get", "remote.origin.url"]
            ),
        }

    def get_file_blame(self, file_path: str) -> Dict[int, Dict]:
        """Get blame information for each line in a file"""
        rel_path = os.path.relpath(file_path, self.repo_path)
        blame_output = self._run_git_command(["blame", "--line-porcelain", rel_path])

        blame_data = {}
        current_commit = None
        line_num = 1

        for line in blame_output.split("\n"):
            if line.startswith("^") or (len(line) > 8 and line[8] == " "):
                # New commit hash
                current_commit = line.split()[0].lstrip("^")
            elif line.startswith("author "):
                author = line[7:]
            elif line.startswith("author-time "):
                timestamp = int(line[12:])
                date = datetime.fromtimestamp(timestamp)
            elif line.startswith("\t"):
                # This is the actual source line
                if current_commit:
                    blame_data[line_num] = {
                        "commit": current_commit,
                        "author": author,
                        "date": date,
                        "line": line[1:],  # Remove the tab
                    }
                line_num += 1

        return blame_data
