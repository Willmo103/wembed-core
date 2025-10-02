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

    debug: bool = Field(
        default_factory=lambda: False if get_environment() == "production" else True,
        description="Enable or disable debug mode.",
    )

    @computed_field(return_type=Path)
    def app_data(self) -> Path:
        """
        Determine the application data directory based on the environment.
        In development or testing, it points to a local 'data' directory.
        In production, it points to a hidden directory in the user's home.
        1. Development/Testing: ./data
        2. Production: ~/.wembed
        """
        if self.debug:
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
        if self.debug:
            return "localhost"
        return env.get("COMPUTERNAME", env.get("HOSTNAME", "localhost")) or "localhost"

    @computed_field(return_type=str)
    def user(self) -> str:
        """
        Determine the user for the application.
        Defaults to the current system user if not set in environment variables.
        """
        if self.debug:
            return "user"
        return env.get("USERNAME", env.get("USER", "unknown")) or "user"

    @computed_field(return_type=str)
    def sqlalchemy_uri(self) -> str:
        """
        Determine the SQLAlchemy database URI.
        Defaults to a SQLite database in the application data directory if not set.
        """
        if self.debug or not env.get("SQLALCHEMY_URI"):
            pth = Path(self.app_data.as_posix())
            return f"sqlite:///{pth / 'wembed.db'}"
        return env["SQLALCHEMY_URI"]

    @computed_field(return_type=str)
    def ollama_url(self) -> str:
        """
        Determine the Ollama URL to set as Ollama env OLLAMA_HOST
        Hierarchical resolution:
        1: In development/testing, use TEST_OLLAMA_HOST if set
        2: Ollama default Environment variable OLLAMA_HOST if set
        3: Default to 'http://localhost:11434'
        """
        if self.debug:
            if "TEST_OLLAMA_HOST" in env:
                return env["TEST_OLLAMA_HOST"]
        if not self.debug:
            if "OLLAMA_HOST" in env:
                return env["OLLAMA_HOST"]
        return "http://localhost:11434"

    def ensure_paths(self) -> None:
        """
        Ensure that the application paths exist, creating them if necessary.
        Returns True if paths exist or were created successfully, False otherwise.
        """
        self.app_data.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


class GotifyConfig(BaseModel):
    """
    Configuration model for Gotify notification service.
    """

    url: str = Field(..., description="Base URL of the Gotify server")
    token: str = Field(..., description="API token for authenticating with Gotify")


__all__ = ["AppConfig", "GotifyConfig"]
