from . import models  # noqa:F401
from .config import *  # noqa:F401, F403
from .database import *  # noqa:F401, F403
from .embedding import EmbeddingModelConfig, EmbeddingService  # noqa:F401, F403
from .file_scanner import *  # noqa:F401, F403
from .services import *  # noqa:F401, F403

__version__ = "0.1.7"
__author__ = "Will Morris"
__license__ = ""
__doc__ = """wembed_core
~~~~~~~~~~~~~~~~~~~~~~~
A core library for context parsing and embedding functionalities.
It includes database models, schemas, and controllers.
It provides foundational utilities for working with text and embeddings.
It also includes controller/repository classes for interacting with the database models.
It supports indexing and embedding functionalities.
It is designed to be used as a backend for applications requiring text processing and embedding capabilities.
"""
