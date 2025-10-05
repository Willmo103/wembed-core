import pytest

from wembed_core.config import AppConfig
from wembed_core.embedding import EmbeddingModelConfig, EmbeddingService
from wembed_core.ollama_client import OllamaClient


class TestEmbeddingService:
    @pytest.fixture
    def app_config(self):
        return AppConfig()

    @pytest.fixture
    def client(self, app_config):
        return OllamaClient(app_config)

    @pytest.fixture
    def embedding_model_config(self):
        return EmbeddingModelConfig()

    @pytest.fixture
    def embedding_service(self, client):
        return EmbeddingService(
            OllamaClient=client,
            embedding_model_config=EmbeddingModelConfig(),
        )

    def test_get_embedding(self, embedding_service: EmbeddingService):
        text = "This is a test."
        embedding = embedding_service.get_embedding(text)
        assert isinstance(embedding, list)
        assert all(isinstance(x, float) for x in embedding[0])
        assert len(embedding[0]) == embedding_service.embedding_config.embedding_length

    def test_default_model_name(self, embedding_service: EmbeddingService):
        assert embedding_service.embedding_config.model_name == "embeddinggemma"

    def test_embedding_length(self, embedding_service: EmbeddingService):
        assert embedding_service.embedding_config.embedding_length == 768

    def test_max_tokens(self, embedding_service: EmbeddingService):
        assert embedding_service.embedding_config.max_tokens == 2048

    def test_hf_model_id(self, embedding_service: EmbeddingService):
        assert (
            embedding_service.embedding_config.hf_model_id
            == "google/embeddinggemma-300m"
        )
