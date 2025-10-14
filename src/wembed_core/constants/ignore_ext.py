"""
wembed_core/constants/ignore_ext.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
File extensions to ignore during file processing.
"""

from typing import Set

IGNORE_EXTENSIONS: Set[str] = {
    ".pyc",
    ".pyo",
    ".db",
    ".sqlite",
    ".log",
    ".DS_Store",
    ".lock",
    ".dll",
    ".exe",
    ".lnk",
    "Thumbs.db",
    ".tmp",
    ".bak",
    ".swp",
    ".pyd",
    ".egg",
    ".egg-info",
    ".pkl",
    ".pickle",
    ".so",
    ".dylib",
    ".o",
    ".a",
    ".lib",
    ".obj",
    ".class",
    ".jar",
    ".war",
    ".ear",
    ".zip",
    ".tar",
    ".tar.gz",
    ".tgz",
    ".gz",
    ".bz2",
    ".xz",
    ".7z",
    ".rar",
    ".iso",
}
