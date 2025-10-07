from os import environ as env
from pathlib import Path

import wembed_core as wbc
import wembed_core.config  # Import config to access helper functions if needed
import wembed_core.embedding


class TestAppConfig:
    # ... (Your backup, clear_env, and restore_env methods are fine) ...
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
        assert config.debug is False
        self.restore_env()

    def test_default_app_config_when_env_is_production(self):
        self.clear_env()
        config = wbc.AppConfig()
        assert config.debug is False
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
        self.restore_env()

    def test_debug(self):
        self.clear_env()
        # The new logic correctly handles being instantiated with debug=True
        config = wbc.AppConfig(debug=True)
        assert config.debug is True

        # Use the source function to get the expected root for consistency
        expected_root = wbc.config.application_root()

        assert config.app_data == expected_root / "data"
        assert config.app_data.name == "data"
        assert config.logs_dir == config.app_data / "logs"
        assert config.logs_dir.name == "logs"

        # Construct the expected URI using .as_posix() to match the implementation
        expected_uri = f"sqlite:///{(expected_root / 'data' / 'wembed.db').as_posix()}"
        assert config.sqlalchemy_uri == expected_uri

        assert config.host == "localhost"
        assert config.user == "user"
        self.restore_env()

    def test_sqlalchemy_uri_default(self):
        self.clear_env()
        config = wbc.AppConfig()  # Production mode by default

        # FIX: Use .as_posix() to ensure the expected URI uses forward slashes,
        # which will match the implementation and pass on all operating systems.
        expected_db_path = Path.home() / ".wembed" / "wembed.db"
        expected_uri = f"sqlite:///{expected_db_path.as_posix()}"

        assert config.sqlalchemy_uri == expected_uri
        self.restore_env()

    def test_sqlalchemy_uri_with_env(self):
        self.clear_env()
        # FIX: Set DEV=true. The new logic correctly scopes the SQLALCHEMY_URI
        # override to only apply during development to prevent accidents.
        env["DEV"] = "true"
        env["SQLALCHEMY_URI"] = "postgresql://user:password@localhost/dbname"

        # Instantiate the config *after* setting the environment
        config = wbc.AppConfig()

        assert config.sqlalchemy_uri == "postgresql://user:password@localhost/dbname"
        self.restore_env()

    # ... (the rest of your tests should be fine) ...
    def test_debug_values(self):
        self.clear_env()
        true_values = ["true", "1", "t", "TRUE", "T", "TrUe"]
        false_values = ["false", "0", "f", "FALSE", "F", "FaLsE"]

        for val in true_values:
            env["DEV"] = val
            config = wbc.AppConfig()
            assert config.debug is True
            self.clear_env()

        for val in false_values:
            env["DEV"] = val
            config = wbc.AppConfig()
            assert config.debug is False
            self.clear_env()
        self.restore_env()

    def test_ensure_paths_returns_true(self):
        self.clear_env()
        # Use debug mode to create paths in the project dir, not the user's home
        config = wbc.AppConfig(debug=True)
        assert config.app_data.exists()
        assert config.logs_dir.exists()
        self.restore_env()

    def test_ollama_host_default(self):
        self.clear_env()
        config = wbc.AppConfig()
        assert config.ollama_url == "http://localhost:11434"
        self.restore_env()

    def test_ollama_host_with_ollama_env(self):
        self.clear_env()

        # test with OLLAMA_HOST in production
        env["OLLAMA_HOST"] = "http://ollama-host:1234"
        config = wbc.AppConfig()
        assert config.debug is False
        assert config.ollama_url == "http://ollama-host:1234"
        self.clear_env()

        # test with DEV mode and TEST_OLLAMA_HOST
        env["DEV"] = "true"
        env["TEST_OLLAMA_HOST"] = "http://test-ollama-host:5678"
        config = wbc.AppConfig()
        assert config.debug is True
        assert config.ollama_url == "http://test-ollama-host:5678"
        self.clear_env()

        # test with no dev and no TEST_OLLAMA_HOST or OLLAMA_HOST
        config = wbc.AppConfig()
        assert config.ollama_url == "http://localhost:11434"
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
