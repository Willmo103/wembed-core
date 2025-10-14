"""
wembed_core/enums.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Enums used throughout the application.
"""

from enum import Enum


class CodeChunkerDependancyTypes(str, Enum):
    """
    Enum for the types of dependencies that can be used for code chunking.
    "stdlib", "local", "external"

    Values:
      STD_LIB: "stdlib"
      LOCAL: "local"
      EXTERNAL: "external"
    """

    STD_LIB = "stdlib"
    LOCAL = "local"
    EXTERNAL = "external"


class CodeChunkerChunkTypes(str, Enum):
    """
    Enum for the types of code chunks.
    "function", "class", "method", "import", "module"

    Values:
      FUNCTION: "function"
      CLASS: "class"
      METHOD: "method"
      IMPORT: "import"
      MODULE: "module"
    """

    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    IMPORT = "import"
    MODULE = "module"
