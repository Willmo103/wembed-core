# import llm_ollama  # noqa: F401 # Ensure the Ollama integration is loaded for llm
from pydantic import BaseModel, Field

from wembed_core.ollama_client import OllamaClient

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
        OllamaClient: OllamaClient,
        embedding_model_config: EmbeddingModelConfig,
    ):
        self.ollama_client = OllamaClient
        self.embedding_config = embedding_model_config

    def get_embedding(self, text: str) -> list[list[float]]:
        """
        Generate an embedding for the given text using the specified model.
        """
        return self.ollama_client.client.embed(
            model=self.embedding_config.model_name,
            input=text,
            truncate=False,
        ).embeddings
