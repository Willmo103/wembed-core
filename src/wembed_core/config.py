# src/wembed_core/config.py
"""
Configuration Models for Wembed Core
"""

from os import environ as env
from pathlib import Path

from pydantic import BaseModel, Field, computed_field, model_validator


def application_root() -> Path:
    """
    Determine the application root directory based on the current file's location.
    """
    return Path(__file__).parent.parent.parent.resolve()


def user_data_dir() -> Path:
    """
    Determine the path to the installed user data directory.
    """
    return Path().home() / ".wembed"


def get_environment() -> str:
    """
    Determine the current environment based on environment variables.
    Returns 'production' if neither DEV nor TESTING flags are set.
    """
    dev_flag = env.get("DEV", "false").lower() in ("true", "1", "t")
    testing_flag = env.get("TESTING", "false").lower() in ("true", "1", "t")
    testing_ollama_flag = env.get("TEST_OLLAMA", "false").lower() in ("true", "1", "t")
    # Consider TEST_OLLAMA as part of testing environment
    testing_flag = testing_flag or testing_ollama_flag
    if dev_flag or testing_flag:
        return "development"
    return "production"


class AppConfig(BaseModel):
    """
    Base configuration model with common settings.
    This model uses a validator to set path-related fields based on the 'debug' flag,
    ensuring consistent behavior whether configured by environment variables or direct instantiation.
    """

    debug: bool = Field(
        default_factory=lambda: get_environment() == "development",
        description="Enable or disable debug mode.",
    )
    # The following fields have dummy defaults; they will be correctly
    # set by the model_validator after 'debug' is resolved.
    app_data: Path = Field(
        default=Path(),
        description="""
        The application data directory.
        1. Development/Testing: ./data
        2. Production: ~/.wembed
        """,
    )
    logs_dir: Path = Field(
        default=Path(),
        description="logs directory based on the application data directory",
    )
    sqlalchemy_uri: str = Field(
        default="",
        description="""
        The SQLAlchemy database URI.
        Defaults to a SQLite database in the application data directory.
        Can be overridden by the SQLALCHEMY_URI env var in development mode.
        """,
    )
    ollama_url: str = Field(
        default_factory=lambda: (
            env.get("TEST_OLLAMA_HOST", "http://localhost:11434")
            if get_environment() == "development"
            else env.get("OLLAMA_HOST", "http://localhost:11434")
        ),
        description="""
        The Ollama URL to set as Ollama env OLLAMA_HOST.
        Hierarchical resolution:
        1: In development/testing, use TEST_OLLAMA_HOST if set
        2: Ollama default Environment variable OLLAMA_HOST if set
        3: Default to 'http://localhost:11434'
        """,
    )

    @model_validator(mode="after")
    def set_dependent_fields(self) -> "AppConfig":
        """
        Sets configuration fields that depend on the final value of 'debug' after the model is initialized.
        """
        # Set app_data path based on the final debug status
        if self.debug:
            self.app_data = application_root() / "data"
        else:
            self.app_data = user_data_dir()

        # Set logs_dir based on the final app_data path
        self.logs_dir = self.app_data / "logs"

        # Set sqlalchemy_uri, allowing override from env var only in debug mode
        if self.debug and "SQLALCHEMY_URI" in env:
            self.sqlalchemy_uri = env["SQLALCHEMY_URI"].replace("\\", "/")
        else:
            db_path = self.app_data / "wembed.db"
            # Use .as_posix() to ensure forward slashes for a valid URI
            self.sqlalchemy_uri = f"sqlite:///{db_path.as_posix()}"

        # Ensure all necessary directories exist
        self.ensure_paths()
        return self

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
        return env.get("USERNAME", env.get("USER", "user")) or "user"

    def ensure_paths(self) -> None:
        """
        Ensure that the application paths exist, creating them if necessary.
        """
        self.app_data.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)


class GotifyConfig(BaseModel):
    """
    Configuration model for Gotify notification service.
    """

    url: str = Field(..., description="Base URL of the Gotify server")
    token: str = Field(..., description="API token for authenticating with Gotify")


__all__ = ["AppConfig", "GotifyConfig", "get_environment"]
