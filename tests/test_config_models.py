from os import environ as env
from pathlib import Path

import wembed_core as wbc


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
        assert config.app_data == Path(__file__).parent.parent / "data"
        assert config.app_data.name == "data"
        assert config.app_data.is_dir()
        assert config.logs_dir == config.app_data / "logs"
        assert config.logs_dir.name == "logs"
        assert config.logs_dir.is_dir()
        assert config.sqlalchemy_uri == "sqlite:///" + str(
            config.app_data / "wembed.db"
        )
        del config
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


class TestEmbeddingModelConfig:

    def test_setting_parameters(self):
        config = wbc.EmbeddingModelConfig(
            model_name="test_model",
            hf_model_id="test/hf-model-id",
            embedding_length=768,
            max_tokens=512,
        )
        assert config.model_name == "test_model"
        assert config.hf_model_id == "test/hf-model-id"
        assert config.embedding_length == 768
        assert config.max_tokens == 512
        del config

    def test_default_parameters(self):
        config = wbc.EmbeddingModelConfig()
        assert config.model_name == "embeddinggemma"
        assert config.hf_model_id == "google/embeddinggemma-300m"
        assert config.embedding_length == 768
        assert config.max_tokens == 2048
        del config
