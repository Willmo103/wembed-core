import fnmatch
import subprocess
from pathlib import Path
from typing import List, Optional

from typer import Exit, echo

from wembed_core.constants import IGNORE_LIST


def get_git_files(repo_path: Path, include_empty: bool = False) -> List[str]:
    """Get list of files tracked by git in the repository, optionally filtering empty files."""
    try:
        result = subprocess.run(
            ["git", "-C", str(repo_path), "ls-files"],
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.splitlines() if f.strip()]

        if not include_empty:
            # Filter out empty files
            non_empty_files = []
            for file_path in files:
                if any(ign in file_path for ign in IGNORE_LIST):
                    continue
                full_path = repo_path / file_path
                try:
                    if full_path.exists() and full_path.stat().st_size > 0:
                        non_empty_files.append(file_path)
                except Exception:
                    # If we can't check the file, include it anyway
                    non_empty_files.append(file_path)
            files = non_empty_files

        return files
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving git files: {e}")
        return []


def apply_filters(
    files: List[str], match_patterns: List[str], exclude_patterns: List[str]
) -> List[str]:
    """Apply match and exclude patterns to filter files using set intersection/difference."""
    file_set = set(files)

    # Apply match patterns (if any) - only include files that match at least one pattern
    if match_patterns:
        matched_files = set()
        for pattern in match_patterns:
            pattern_matches = {f for f in file_set if fnmatch.fnmatch(f, pattern)}
            matched_files.update(pattern_matches)
        file_set = file_set.intersection(matched_files)

    # Apply exclude patterns - remove files that match any exclude pattern
    if exclude_patterns:
        excluded_files = set()
        for pattern in exclude_patterns:
            pattern_matches = {f for f in file_set if fnmatch.fnmatch(f, pattern)}
            excluded_files.update(pattern_matches)
        file_set = file_set.difference(excluded_files)

    return sorted(list(file_set))


def build_tree_structure(files: List[str] | List[Path]) -> str:
    """Build a tree structure string from a list of file paths."""
    if not files:
        return ""

    if isinstance(files[0], Path):
        files = [str(f.as_posix()) for f in files]

    # Build directory structure
    tree_dict = {}
    for file_path in sorted(files):
        parts = file_path.split("/")
        current = tree_dict

        for i, part in enumerate(parts):
            if i == len(parts) - 1:  # It's a file
                if "__files__" not in current:
                    current["__files__"] = []
                current["__files__"].append(part)
            else:  # It's a directory
                if part not in current:
                    current[part] = {}
                current = current[part]

    # Convert tree_dict to tree string
    def render_tree(node: dict, prefix: str = "", is_last: bool = True) -> List[str]:
        lines = []

        # Collect directories
        dirs = [
            (k, v) for k, v in node.items() if k != "__files__" and isinstance(v, dict)
        ]
        dirs.sort(key=lambda x: x[0])

        # Collect files
        files = node.get("__files__", [])
        files.sort()

        # Combine directories and files
        all_items = [(name, "dir", content) for name, content in dirs] + [
            (name, "file", None) for name in files
        ]

        for i, (name, item_type, content) in enumerate(all_items):
            is_last_item = i == len(all_items) - 1

            if item_type == "dir":
                symbol = "└── " if is_last_item else "├── "
                lines.append(f"{prefix}{symbol}{name}/")

                next_prefix = prefix + ("    " if is_last_item else "│   ")
                lines.extend(render_tree(content, next_prefix, is_last_item))
            else:
                symbol = "└── " if is_last_item else "├── "
                lines.append(f"{prefix}{symbol}{name}")

        return lines

    if not tree_dict:
        return ""

    # Start with root directory
    root_lines = []
    if len(tree_dict) == 1 and "__files__" not in tree_dict:
        # Single root directory
        root_name = list(tree_dict.keys())[0]
        root_lines.append(f"{root_name}/")
        root_lines.extend(render_tree(tree_dict[root_name], "   "))
    else:
        # Multiple items at root or files at root
        root_lines.extend(render_tree(tree_dict))

    return "\n".join(root_lines)


def write_output(
    content: str, file_path: Optional[Path], encoding: str, print_output: bool
):
    """Write content to file and/or stdout based on options.

    Args:
        content: [str] The content to write.
        file_path: [pathlib.Path] Optional path to write the content to. If None, only prints to stdout.
        encoding: [str] The encoding to use when writing to file or printing.
        print_output: [bool] Whether to print the content to stdout.
    """

    if print_output:
        if encoding != "utf8":
            content = content.encode(encoding, errors="ignore").decode(
                encoding, errors="ignore"
            )
        echo(content)

    if file_path:
        try:
            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
            if not print_output:  # Only show file message if not printing to stdout
                echo(f"Output written to: {file_path}")
        except Exception as e:
            echo(f"Error writing to file {file_path}: {e}", err=True)
            raise Exit(1)
