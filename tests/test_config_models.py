from pathlib import Path

import pytest

import wembed_core as wbc
from os import environ as env

class TestAppConfig:

    def test_environment_default(self):
        # Clear environment variables for this test
        config = wbc.AppConfig()
        assert config.environment == "production"
        del config

    def test_default_app_config_when_env_is_production(self):
        config = wbc.AppConfig()
        assert config.environment == "production"
        assert config.app_data == Path.home() / ".wembed"
        assert config.app_data.name == ".wembed"
        assert config.app_data.is_dir()
        assert config.logs_dir == Path.home() / ".wembed" / "logs"
        assert config.logs_dir.name == "logs"
        assert config.logs_dir.is_dir()
        del config


    def test_environment_dev(self):
        env["DEV"] = "true"
        config = wbc.AppConfig()
        assert config.environment == "development"
        del env["DEV"]

    def test_environment_dev_values(self):
        true_values = ["true", "1", "t", "TRUE", "T", "TrUe"]
        false_values = ["false", "0", "f", "FALSE", "F", "FaLsE"]

        for val in true_values:
            env["DEV"] = val
            config = wbc.AppConfig()
            assert config.environment == "development"
            del env["DEV"]
            del config

        for val in false_values:
            env["DEV"] = val
            config = wbc.AppConfig()
            assert config.environment == "production"
            del env["DEV"]
            del config

