from typing import Optional

import llm
from pydantic import BaseModel, Field

from wembed_core import AppConfig


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
        app_config: Optional[AppConfig] = None,
        embedding_config: Optional[EmbeddingModelConfig] = None,
    ):
        if app_config is None or not isinstance(app_config, AppConfig):
            self.config = AppConfig()  # Ensure AppConfig is initialized
        self.app_config = app_config
        if embedding_config is None or not isinstance(
            embedding_config, EmbeddingModelConfig
        ):
            embedding_config = EmbeddingModelConfig()
        self.embedding_config = embedding_config
        self._model: llm.EmbeddingModel = llm.get_embedding_model(
            name=self.embedding_config.model_name,
        )

    def get_embedding(self, text: str) -> list[float]:
        """
        Generate an embedding for the given text using the specified model.
        """
        return self._model.embed(text)
