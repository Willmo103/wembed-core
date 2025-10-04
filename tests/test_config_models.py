from os import environ as env
from pathlib import Path

import wembed_core as wbc
import wembed_core.embedding


class TestAppConfig:

    _backup_dev = env.get("DEV", None)
    _backup_testing = env.get("TESTING", None)
    _backup_sqlalchemy = env.get("SQLALCHEMY_URI", None)
    _backup_ollama = env.get("OLLAMA_HOST", None)
    _backup_test_ollama = env.get("TEST_OLLAMA_HOST", None)

    def clear_env(self):
        if "DEV" in env:
            del env["DEV"]
        if "TESTING" in env:
            del env["TESTING"]
        if "SQLALCHEMY_URI" in env:
            del env["SQLALCHEMY_URI"]
        if "OLLAMA_HOST" in env:
            del env["OLLAMA_HOST"]
        if "TEST_OLLAMA_HOST" in env:
            del env["TEST_OLLAMA_HOST"]

    def restore_env(self):
        if self._backup_dev is not None:
            env["DEV"] = self._backup_dev
        if self._backup_testing is not None:
            env["TESTING"] = self._backup_testing
        if self._backup_sqlalchemy is not None:
            env["SQLALCHEMY_URI"] = self._backup_sqlalchemy
        if self._backup_ollama is not None:
            env["OLLAMA_HOST"] = self._backup_ollama
        if self._backup_test_ollama is not None:
            env["TEST_OLLAMA_HOST"] = self._backup_test_ollama

    def test_environment_default(self):
        self.clear_env()
        config = wbc.AppConfig()
        assert config.debug == False
        del config
        self.clear_env()

    def test_default_app_config_when_env_is_production(self):
        # Clear environment variables for this test
        self.clear_env()
        config = wbc.AppConfig()
        assert config.debug == False
        assert config.app_data == Path.home() / ".wembed"
        assert config.app_data.name == ".wembed"
        assert config.logs_dir == Path.home() / ".wembed" / "logs"
        assert config.logs_dir.name == "logs"
        assert config.sqlalchemy_uri is not None
        assert isinstance(config.sqlalchemy_uri, str)
        assert config.host is not None
        assert isinstance(config.host, str)
        assert config.user is not None
        assert isinstance(config.user, str)
        self.clear_env()

    def test_debug(self):
        self.clear_env()
        config = wbc.AppConfig(debug=True)
        assert config.debug == True
        assert config.app_data == Path(__file__).parent.parent / "data"
        assert config.app_data.name == "data"
        assert config.logs_dir == config.app_data / "logs"
        assert config.logs_dir.name == "logs"
        assert config.sqlalchemy_uri == "sqlite:///" + str(
            config.app_data / "wembed.db"
        ).replace(
            "\\", "/"
        )  # noqa
        assert config.host == "localhost"
        assert config.user == "user"
        del config
        self.restore_env()

    def test_sqlalchemy_uri_default(self):
        self.clear_env()
        config = wbc.AppConfig()
        expected_uri = f"sqlite:///{(Path(config.app_data.as_posix()) / 'wembed.db')}"
        assert config.sqlalchemy_uri == expected_uri
        del config
        self.restore_env()

    def test_sqlalchemy_uri_with_env(self):
        self.clear_env()
        env["SQLALCHEMY_URI"] = "postgresql://user:password@localhost/dbname"
        config = wbc.AppConfig(debug=False)
        assert config.sqlalchemy_uri == "postgresql://user:password@localhost/dbname"
        del env["SQLALCHEMY_URI"]
        del config
        self.restore_env()

    def test_debug_values(self):
        self.clear_env()
        true_values = ["true", "1", "t", "TRUE", "T", "TrUe"]
        false_values = ["false", "0", "f", "FALSE", "F", "FaLsE"]

        for val in true_values:
            env["DEV"] = val
            config = wbc.AppConfig()
            assert config.debug == True
            del config
            self.clear_env()

        for val in false_values:
            env["DEV"] = val
            config = wbc.AppConfig()
            assert config.debug == False
            del config
            self.clear_env()

    def test_ensure_paths_returns_true(self):
        self.clear_env()
        config = wbc.AppConfig()
        config.ensure_paths()
        assert config.app_data.exists()
        assert config.logs_dir.exists()
        del config
        self.clear_env()
        self.restore_env()

    def test_ollama_host_default(self):
        self.clear_env()
        config = wbc.AppConfig()
        assert config.ollama_url == "http://localhost:11434"
        del config
        self.restore_env()

    def test_ollama_host_with_ollama_env(self):
        host = env.get("OLLAMA_HOST", None)
        self.clear_env()
        env["OLLAMA_HOST"] = "http://ollama-host:1234"
        config = wbc.AppConfig()
        assert config.debug == False
        assert config.ollama_url == "http://ollama-host:1234"
        self.clear_env()
        del config

        # test with DEV mode and TEST_OLLAMA_HOST
        env["DEV"] = "true"
        env["TEST_OLLAMA_HOST"] = "http://test-ollama-host:5678"
        config = wbc.AppConfig()
        assert config.debug == True
        assert config.ollama_url == "http://test-ollama-host:5678"
        self.clear_env()
        del config

        # test with no dev and no TEST_OLLAMA_HOST or OLLAMA_HOST
        config = wbc.AppConfig()
        assert config.ollama_url == "http://localhost:11434"
        del config
        self.clear_env()
        self.restore_env()


class TestEmbeddingModelConfig:

    def test_setting_parameters(self):
        config = wembed_core.embedding.EmbeddingModelConfig(
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
        config = wembed_core.embedding.EmbeddingModelConfig()
        assert config.model_name == "embeddinggemma"
        assert config.hf_model_id == "google/embeddinggemma-300m"
        assert config.embedding_length == 768
        assert config.max_tokens == 2048
        del config


class TestGotifyModelConfig:

    def test_setting_parameters(self):
        config = wbc.GotifyConfig(
            url="http://localhost:8080",
            token="test_token",
        )
        assert config.url == "http://localhost:8080"
        assert config.token == "test_token"
        del config

    def test_missing_parameters(self):
        try:
            wbc.GotifyConfig()
        except Exception as e:
            assert isinstance(e, ValueError)
        else:
            assert False, "ValueError was not raised for missing parameters"
