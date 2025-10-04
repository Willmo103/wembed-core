import os

import llm

# import llm_ollama  # noqa: F401 # Ensure the Ollama integration is loaded for llm
from pydantic import BaseModel, Field

from wembed_core import AppConfig

# from typing import Optional


class EmbeddingModelConfig(BaseModel):
    """
    Configuration model for embedding model settings.
    """

    model_name: str = Field(default="embeddinggemma")
    hf_model_id: str = Field(default="google/embeddinggemma-300m")
    embedding_length: int = Field(default=768)
    max_tokens: int = Field(default=2048)


class EmbeddingService:
    """
    Service class for managing embedding model configurations.
    """

    def __init__(
        self,
        app_config: AppConfig = AppConfig(),
        embedding_model_config: EmbeddingModelConfig = EmbeddingModelConfig(),
    ):
        try:
            import llm_ollama  # noqa: F401 # Ensure the Ollama integration is loaded for llm

            self.app_config = app_config
            self.embedding_config = embedding_model_config
            os.environ["OLLAMA_HOST"] = self.app_config.ollama_url
            self._model: llm.EmbeddingModel = llm.get_embedding_model(
                name=self.embedding_config.model_name,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to initialize EmbeddingService: {e}")

    def get_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding for the given text using the specified model.
        """
        return self._model.embed(text)
