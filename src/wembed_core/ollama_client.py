"""
wembed_core/ollama_client.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Client wrapper for interacting with the Ollama API.
"""

from ollama import Client

from .config import AppConfig


class OllamaClient:
    def __init__(self, app_config: AppConfig):
        self.host = app_config.ollama_url
        self.client = Client(host=self.host)


# class AsyncOllamaClient:
#     def __init__(self, app_config: AppConfig):
#         self.host = app_config.ollama_url
#         self.client = AsyncClient(host=self.host)
