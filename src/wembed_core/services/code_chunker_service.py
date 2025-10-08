"""
wembed_core/services/code_chunker_service.py

Orchestrates the code chunking process for an indexed repository.
"""


from wembed_core.chunker.ast_chunker import ASTChunker
from wembed_core.controllers import (
    CodeChunkerCodeChunksController,
    IndexedFileController,
    IndexedRepoController,
)
from wembed_core.database import DatabaseService


class CodeChunkerService:
    """
    A service to analyze and chunk the files within an indexed repository.
    """

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.repo_controller = IndexedRepoController(db_service)
        self.file_controller = IndexedFileController(db_service)
        self.chunk_controller = CodeChunkerCodeChunksController(db_service)

    def process_repository(self, repo_id: int) -> int:
        """
        Chunks all Python files in a given repository.

        Args:
            repo_id (int): The ID of the IndexedRepo to process.

        Returns:
            int: The number of chunks created.
        """
        repo = self.repo_controller.get_by_id(repo_id)
        if not repo:
            print(f"Error: Repository with ID {repo_id} not found.")
            return 0

        # Get all files associated with this repository from the IndexedFiles table
        files_to_process = self.file_controller.get_by_source_name(
            repo.repo_name
        )

        python_files = [f for f in files_to_process if f.path.endswith(".py")]

        print(
            f"Found {len(python_files)} Python files to chunk for repo '{repo.repo_name}'."
        )

        total_chunks_created = 0
        for file_record in python_files:
            print(f"  - Chunking {file_record.path}...")
            chunker = ASTChunker(file_path=file_record.path)
            code_chunks = chunker.chunk()

            if code_chunks:
                # Use the controller to save the chunks to the database
                self.chunk_controller.create_batch(code_chunks)
                total_chunks_created += len(code_chunks)

        print(
            f"Finished processing. Created {total_chunks_created} total chunks."
        )
        return total_chunks_created
