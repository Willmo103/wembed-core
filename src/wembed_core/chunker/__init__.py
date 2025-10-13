"""
Chunker module for various chunking strategies.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module includes different chunking strategies such as AST-based chunking, dependency-based chunking, and Git metadata extraction.
"""

from .ast_chunker import ASTChunker  # noqa: F401, F403
from .dependency_analyzer import DependencyAnalyzer  # noqa: F401, F403
from .git_metadata_extractor import GitMetadataExtractor  # noqa: F401, F403

__all__ = ["ASTChunker", "DependencyAnalyzer", "GitMetadataExtractor"]
