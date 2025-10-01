"""
tests/test_schemas/test_indexed_repo_schema.py
Pytest tests for IndexedRepoSchema Pydantic model.
"""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from wembed_core.schemas import IndexedRepoSchema
