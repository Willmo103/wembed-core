"""
Configuration Models for Wembed Core
"""

from os import environ as env
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, computed_field


def get_environment() -> str:
    """
    Determine the current environment based on environment variables.
    Returns 'production' if neither DEV nor TESTING flags are set.
    """
    dev_flag = env.get("DEV", "false").lower() in ("true", "1", "t")
    testing_flag = env.get("TESTING", "false").lower() in ("true", "1", "t")
    if dev_flag or testing_flag:
        return "development"
    return "production"


class AppConfig(BaseModel):
    """
    Base configuration model with common settings.
    """

    @computed_field
    def environment(self) -> str:
        """
        Determine the current environment based on environment variables.
        Returns 'production' if neither DEV nor TESTING flags are set.
        """
        return get_environment()

    @computed_field
    def app_data(self) -> Path:
        """
        Determine the application data directory based on the environment.
        In development or testing, it points to a local 'data' directory.
        In production, it points to a hidden directory in the user's home.
        1. Development/Testing: ./data
        2. Production: ~/.wembed
        """
        _env = get_environment()
        if _env == "development" or _env == "testing":
            return Path(__file__).parent.parent.parent / "data"
        return Path.home() / ".wembed"

    @computed_field
    def logs_dir(self) -> Path:
        """
        Determine the logs directory based on the application data directory.
        """
        return self.app_data / "logs"

    @computed_field
    def host(self) -> str:
        """
        Determine the host for the application.
        Defaults to 'localhost' if not set in environment variables.
        """
        return env.get("COMPUTERNAME", env.get("HOSTNAME", "localhost")) or "localhost"

    @computed_field
    def user(self) -> str:
        """
        Determine the user for the application.
        Defaults to the current system user if not set in environment variables.
        """
        return env.get("USERNAME", env.get("USER", "unknown")) or "user"

    @computed_field
    def sqlalchemy_uri(self) -> str:
        """
        Determine the SQLAlchemy database URI.
        Defaults to a SQLite database in the application data directory if not set.
        """
        return env.get(
            "SQLALCHEMY_DB_URI",
            f"sqlite:///{self.app_data / 'wembed.db'}".replace("\\", "/"),
        )

    @computed_field
    def hugging_face_token(self) -> Optional[str]:
        """
        Retrieve the Hugging Face API token from environment variables, if set.
        """
        return env.get("HF_TOKEN", None)

    def ensure_directories(self) -> None:
        """
        Ensure that the application data and logs directories exist.
        """
        self.app_data.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


class EmbeddingModelConfig(BaseModel):
    """
    Configuration model for embedding model settings.
    """

    model_name: str
    hf_model_id: str
    embedding_length: int
    max_tokens: int

    @classmethod
    def default(cls) -> "EmbeddingModelConfig":
        """
        Provide default settings for the embedding model.
        :return:
        An instance of EmbeddingModelConfig with default values.
        1. model_name: 'embeddinggemma'
        2. hf_model_id: 'google/embeddinggemma-300m'
        3. embedding_length: 768
        4. max_tokens: 2048
        """
        return cls(
            model_name="embeddinggemma",
            hf_model_id="google/embeddinggemma-300m",
            embedding_length=768,
            max_tokens=2048,
        )

__all__ = ["AppConfig", "EmbeddingModelConfig"]

if __name__ == "__main__":
    env["DEV"] = "true"  # For testing purposes
    config = AppConfig()
    print("Environment:", config.environment)
    print("App Data Directory:", config.app_data)
    print("Logs Directory:", config.logs_dir)
    print("Host:", config.host)
    print("User:", config.user)
    print("SQLAlchemy URI:", config.sqlalchemy_uri)
    print("Hugging Face Token:", config.hugging_face_token)
    config.ensure_directories()
    embedding_config = EmbeddingModelConfig.default()
    print("Default Embedding Model Config:", embedding_config.model_dump_json(indent=2))
