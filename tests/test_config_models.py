from os import environ as env
from pathlib import Path

import wembed_core as wbc


class TestAppConfig:

    def test_environment_default(self):
        dev_bak = None
        if "DEV" in env:
            dev_bak = env["DEV"]
            del env["DEV"]
        testing_bak = None
        if "TESTING" in env:
            testing_bak = env["TESTING"]
            del env["TESTING"]
        # Clear environment variables for this test
        config = wbc.AppConfig()
        assert config.debug == False
        del config
        if dev_bak is not None:
            env["DEV"] = dev_bak
            del dev_bak
        if testing_bak is not None:
            env["TESTING"] = testing_bak
            del testing_bak

    def test_default_app_config_when_env_is_production(self):
        # Clear environment variables for this test
        dev_bak = None
        if "DEV" in env:
            dev_bak = env["DEV"]
            del env["DEV"]
        testing_bak = None
        if "TESTING" in env:
            testing_bak = env["TESTING"]
            del env["TESTING"]
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
        if dev_bak is not None:
            env["DEV"] = dev_bak
            del dev_bak
        if testing_bak is not None:
            env["TESTING"] = testing_bak
            del testing_bak
        del config

    def test_debug(self):
        config = wbc.AppConfig(debug=True)
        assert config.debug == True
        assert config.app_data == Path(__file__).parent.parent / "data"
        assert config.app_data.name == "data"
        assert config.logs_dir == config.app_data / "logs"
        assert config.logs_dir.name == "logs"
        assert config.sqlalchemy_uri == "sqlite:///" + str(
            config.app_data / "wembed.db"
        )
        assert config.host == "localhost"
        assert config.user == "user"
        del config

    def test_sqlalchemy_uri_default(self):
        dev_bak = None
        sqlalchemy_bak = None
        if "DEV" in env:
            dev_bak = env["DEV"]
            del env["DEV"]
        if "SQLALCHEMY_URI" in env:
            sqlalchemy_bak = env["SQLALCHEMY_URI"]
            del env["SQLALCHEMY_URI"]
        config = wbc.AppConfig()
        expected_uri = f"sqlite:///{Path(config.app_data.as_posix()) / 'wembed.db'}"
        assert config.sqlalchemy_uri == expected_uri
        if dev_bak is not None:
            env["DEV"] = dev_bak
            del dev_bak
        del config

    def test_sqlalchemy_uri_with_env(self):
        dev_bak = None
        if "DEV" in env:
            dev_bak = env["DEV"]
            del env["DEV"]
        env["SQLALCHEMY_URI"] = "postgresql://user:password@localhost/dbname"
        config = wbc.AppConfig()
        assert config.sqlalchemy_uri == "postgresql://user:password@localhost/dbname"
        del env["SQLALCHEMY_URI"]
        if dev_bak is not None:
            env["DEV"] = dev_bak
            del dev_bak
        del config

    def test_debug_values(self):
        true_values = ["true", "1", "t", "TRUE", "T", "TrUe"]
        false_values = ["false", "0", "f", "FALSE", "F", "FaLsE"]
        dev_bak = None

        for val in true_values:
            env["DEV"] = val
            config = wbc.AppConfig()
            assert config.debug == True
            del env["DEV"]
            del config

        for val in false_values:
            env["DEV"] = val
            config = wbc.AppConfig()
            assert config.debug == False
            del env["DEV"]
            del config

    def test_ensure_paths_returns_true(self):
        dev_bak = None
        if "DEV" in env:
            dev_bak = env["DEV"]
            del env["DEV"]

        env["DEV"] = "true"
        config = wbc.AppConfig()
        config.ensure_paths()
        assert config.app_data.exists()
        assert config.logs_dir.exists()
        del env["DEV"]

        if dev_bak is not None:
            env["DEV"] = dev_bak
            del dev_bak

        del config

    def test_ollama_host_default(self):
        host = env.get("OLLAMA_HOST", None)
        bak_host = None
        bak_test = None
        bak_dev = None
        if host is not None:
            bak_host = host
            del env["OLLAMA_HOST"]
        if "TEST_OLLAMA_HOST" in env:
            bak_test = env["TEST_OLLAMA_HOST"]
            del env["TEST_OLLAMA_HOST"]
        if "DEV" in env:
            bak_dev = env["DEV"]
            del env["DEV"]
        config = wbc.AppConfig()
        assert config.ollama_url == "http://localhost:11434"
        if bak_host is not None:
            env["OLLAMA_HOST"] = bak_host
        if bak_test is not None:
            env["TEST_OLLAMA_HOST"] = bak_test
        if bak_dev is not None:
            env["DEV"] = bak_dev
        del bak_host
        del bak_test
        del bak_dev
        del config

    def test_ollama_host_with_ollama_env(self):
        host = env.get("OLLAMA_HOST", None)
        bak_host = None
        bak_test = None
        bak_dev = None
        if host is not None:
            bak_host = host
            del env["OLLAMA_HOST"]
        if "TEST_OLLAMA_HOST" in env:
            bak_test = env["TEST_OLLAMA_HOST"]
            del env["TEST_OLLAMA_HOST"]
        if "DEV" in env:
            bak_dev = env["DEV"]
            del env["DEV"]
        env["OLLAMA_HOST"] = "http://ollama-host:1234"
        config = wbc.AppConfig()
        assert config.debug == False
        assert config.ollama_url == "http://ollama-host:1234"
        del env["OLLAMA_HOST"]
        del config

        # test with DEV mode and TEST_OLLAMA_HOST
        env["DEV"] = "true"
        env["TEST_OLLAMA_HOST"] = "http://test-ollama-host:5678"
        config = wbc.AppConfig()
        assert config.debug == True
        assert config.ollama_url == "http://test-ollama-host:5678"
        del env["TEST_OLLAMA_HOST"]
        del env["DEV"]
        del config

        # test with no dev and no TEST_OLLAMA_HOST or OLLAMA_HOST
        config = wbc.AppConfig()
        assert config.ollama_url == "http://localhost:11434"
        if bak_host is not None:
            env["OLLAMA_HOST"] = bak_host
        if bak_test is not None:
            env["TEST_OLLAMA_HOST"] = bak_test
        if bak_dev is not None:
            env["DEV"] = bak_dev
        del bak_host
        del bak_test
        del bak_dev
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
