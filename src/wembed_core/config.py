"""
Configuration Models for Wembed Core
"""

from os import environ as env
from pathlib import Path

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

    @computed_field(return_type=str)
    def environment(self) -> str:
        """
        Determine the current environment based on environment variables.
        Returns 'production' if neither DEV nor TESTING flags are set.
        """
        return get_environment()

    @computed_field(return_type=Path)
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

    @computed_field(return_type=Path)
    def logs_dir(self) -> Path:
        """
        Determine the logs directory based on the application data directory.
        """
        return Path(self.app_data.as_posix()) / "logs"  # mypy: ignore

    @computed_field(return_type=str)
    def host(self) -> str:
        """
        Determine the host for the application.
        Defaults to 'localhost' if not set in environment variables.
        """
        if self.environment == "development":
            return "localhost"
        return env.get("COMPUTERNAME", env.get("HOSTNAME", "localhost")) or "localhost"

    @computed_field(return_type=str)
    def user(self) -> str:
        """
        Determine the user for the application.
        Defaults to the current system user if not set in environment variables.
        """
        if self.environment == "development":
            return "user"
        return env.get("USERNAME", env.get("USER", "unknown")) or "user"

    @computed_field(return_type=str)
    def sqlalchemy_uri(self) -> str:
        """
        Determine the SQLAlchemy database URI.
        Defaults to a SQLite database in the application data directory if not set.
        """
        return env.get(
            "SQLALCHEMY_URI",
            f"sqlite:///{Path(self.app_data.as_posix()) / 'wembed.db'}",
        )

    def ensure_paths(self) -> None:
        """
        Ensure that the application paths exist, creating them if necessary.
        Returns True if paths exist or were created successfully, False otherwise.
        """
        self.app_data.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


class EmbeddingModelConfig(BaseModel):
    """
    Configuration model for embedding model settings.
    """

    model_name: str = Field(default="embeddinggemma")
    hf_model_id: str = Field(default="google/embeddinggemma-300m")
    embedding_length: int = Field(default=768)
    max_tokens: int = Field(default=2048)


class GotifyConfig(BaseModel):
    """
    Configuration model for Gotify notification service.
    """

    url: str = Field(..., description="Base URL of the Gotify server")
    token: str = Field(..., description="API token for authenticating with Gotify")


__all__ = ["AppConfig", "EmbeddingModelConfig", "GotifyConfig"]
