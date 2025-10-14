"""
wembed_core/chunker/ast_chunker.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Chunks Python code using AST parsing to identify classes and functions.
This module provides the ASTChunker class which reads a Python file,
parses its AST, and generates code chunks for classes and functions/methods.
It returns a list of CodeChunk schemas representing the identified code segments.
"""

import ast
from typing import List, Optional

from wembed_core.schemas import CodeChunk


class ASTChunker:
    """Chunks Python code from a file path using AST parsing."""

    def __init__(self, file_path: str):
        """
        Initializes the ASTChunker with the given file path.
        Args:
            file_path (str): Path to the Python source code file.
        """
        self.file_path = file_path
        self.source_lines: List[str] = []
        self.tree: Optional[ast.AST] = None

    def _load_source(self) -> bool:
        """
        Reads and parses the source code file.
        Returns:
            bool: True if the file was successfully read and parsed, False otherwise.
        """
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                source = f.read()
            self.source_lines = source.splitlines()
            self.tree = ast.parse(source)
            return True
        except (IOError, SyntaxError) as e:
            print(f"Error processing {self.file_path}: {e}")
            return False

    def chunk(self) -> List[CodeChunk]:
        """
        Orchestrates the chunking process for the file.
        Returns:
            List[CodeChunk]: List of CodeChunk schemas representing the code segments.
        """
        if not self._load_source() or not self.tree:
            return []

        chunks = []
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                chunks.append(self._create_function_chunk(node))
            elif isinstance(node, ast.ClassDef):
                class_chunk, method_chunks = self._create_class_and_method_chunks(node)
                chunks.append(class_chunk)
                chunks.extend(method_chunks)
        return chunks

    def _create_function_chunk(
        self, node: ast.FunctionDef, parent_id: Optional[str] = None
    ) -> CodeChunk:
        """
        Creates a CodeChunk for a function or method.
        Args:
            node (ast.FunctionDef): The AST node representing the function.
            parent_id (Optional[str]): The ID of the parent class if this is a method.
        Returns:
            CodeChunk: The created CodeChunk schema.
        """
        start_line = node.lineno
        end_line = node.end_lineno or start_line

        return CodeChunk(
            content="\n".join(self.source_lines[start_line - 1 : end_line]),
            chunk_type="method" if parent_id else "function",
            file_path=self.file_path,
            start_line=start_line,
            end_line=end_line,
            parent_id=parent_id,
            docstring=ast.get_docstring(node),
        )

    def _create_class_and_method_chunks(
        self, node: ast.ClassDef
    ) -> tuple[CodeChunk, List[CodeChunk]]:
        """
        Creates a CodeChunk for a class and all its methods.
        Args:
            node (ast.ClassDef): The AST node representing the class.
        Returns:
            tuple[CodeChunk, List[CodeChunk]]: The class CodeChunk and a list of method CodeChunks.
        """
        start_line = node.lineno
        first_method_line = node.end_lineno or start_line

        # Find where the class definition ends and methods begin
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                first_method_line = child.lineno
                break

        class_chunk = CodeChunk(
            content="\n".join(
                self.source_lines[start_line - 1 : first_method_line - 1]
            ),
            chunk_type="class",
            file_path=self.file_path,
            start_line=start_line,
            end_line=first_method_line - 1,
            docstring=ast.get_docstring(node),
        )

        method_chunks = [
            self._create_function_chunk(child, parent_id=class_chunk.id)
            for child in node.body
            if isinstance(child, ast.FunctionDef)
        ]

        return class_chunk, method_chunks
