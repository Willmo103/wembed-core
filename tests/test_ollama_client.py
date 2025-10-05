import pytest
from ollama import Client

from wembed_core.config import AppConfig
from wembed_core.ollama_client import OllamaClient


class TestOllamaClient:
    @pytest.fixture
    def app_config(self) -> AppConfig:
        return AppConfig()

    @pytest.fixture
    def ollama_client(self, app_config: AppConfig) -> OllamaClient:
        return OllamaClient(app_config)

    def test_ollama_client_initialization(
        self, ollama_client: OllamaClient, app_config: AppConfig
    ):
        assert ollama_client.host == app_config.ollama_url
        assert isinstance(ollama_client.client, Client)  # Ensure client is initialized
