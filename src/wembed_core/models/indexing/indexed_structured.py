"""
source: src/wembed_core/models/indexing/indexed_structured.py
~~~~~~~~~~~~~~~~~~~~~
SQLAlchemy model for structured data indexing.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, Integer, LargeBinary, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from wembed_core.database import AppBase


class IndexedStructured(AppBase):
    """
    Represents structured data in the database.

    Attributes:
        id (int): Primary key.
        source_name (str): Name of the data source.
