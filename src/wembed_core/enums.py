from enum import Enum


class CodeChunkerDependancyTypes(str, Enum):
    """
    Enum for the types of dependencies that can be used for code chunking.
    """

    STD_LIB = "stdlib"
    LOCAL = "local"
    EXTERNAL = "external"
