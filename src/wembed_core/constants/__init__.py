from .headers import HEADERS  # noqa
from .ignore_ext import IGNORE_EXTENSIONS  # noqa
from .ignore_parts import IGNORE_PARTS  # noqa
from .md_xref import MD_XREF  # noqa
from .stdlib_modules import STD_LIB_MODULES  # noqa

IGNORE_LIST: list[str] = [
    *IGNORE_PARTS,
    ".git",
]

__all__ = [
    "HEADERS",
    "IGNORE_EXTENSIONS",
    "IGNORE_PARTS",
    "MD_XREF",
    "STD_LIB_MODULES",
    "IGNORE_LIST",
]
