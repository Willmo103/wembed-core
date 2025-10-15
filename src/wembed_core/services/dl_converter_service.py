"""
wembed_core/services/dl_converter_service.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Orchestrates the conversion of documents into deep learning-friendly formats and stores them in the database.
"""

from typing import Optional

from wembed_core.config import AppConfig
from wembed_core.database import DatabaseService
from wembed_core.embedding import EmbeddingModelConfig, EmbeddingService
from wembed_core.ollama_client import OllamaClient


class DLConverterService:
    """
    Service to convert documents into deep learning-friendly formats and store them in the database.
    This service handles document conversion, chunking, embedding generation, and database storage.
    """

    from docling.document_converter import DocumentConverter
    from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
    from docling_core.transforms.chunker.tokenizer.huggingface import (
        HuggingFaceTokenizer,
    )
    from docling_core.types.doc.document import DoclingDocument

    def __init__(
        self,
        app_config: AppConfig,
        embedding_model_config: Optional[EmbeddingModelConfig] = EmbeddingModelConfig(),
    ):
        self._temp_dir = app_config.app_data / "dl_temp"
        if not self._temp_dir.exists():
            self._temp_dir.mkdir(parents=True, exist_ok=True)
        self._db_service = DatabaseService(app_config)
        self._ollama_client = OllamaClient(app_config)
        self._embedding_model_config = embedding_model_config
        self._embedding_service = EmbeddingService(
            app_config, embedding_model_config or EmbeddingModelConfig()
        )
        self._document_converter = "DocumentConverter"()
        self._chunker = "HybridChunker"(
            tokenizer="HuggingFaceTokenizer.from_pretrained"(
                model_name=self._embedding_model_config.hf_model_id,
                max_length=self._embedding_model_config.max_tokens,
            ),
            max_tokens=self._embedding_model_config.max_tokens,
            merge_peers=True,
        )
