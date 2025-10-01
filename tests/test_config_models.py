import pytest

from wembed_core.config import AppConfig
from os import environ as env

class TestAppConfig:

    def test_environment_default(self):
        # Clear environment variables for this test
        config = AppConfig()
        assert config.environment == "production"

