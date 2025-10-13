"""
wembed_core/services/file_scanning_service.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Orchestrates the scanning of files within a directory and extracts relevant information.
"""

from pathlib import Path
from typing import List, Optional

from wembed_core.controllers.indexed_file_controller import IndexedFileController
from wembed_core.controllers.indexed_repo_controller import IndexedRepoController
from wembed_core.database import DatabaseService
from wembed_core.schemas.indexing_schemas import (
    IndexedFileSchema,
    IndexedRepoSchema,
    IndexingResultSchema,
)


class FileScanningService:
    pass
