"""
Configuration Models for Wembed Core
"""

from os import environ as env
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, computed_field


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
    if dev_flag or testing_flag:
        return "development"
    return "production"


class AppConfig(BaseModel):
    """
    Base configuration model with common settings.
    """

    debug: bool = Field(
        default_factory=lambda: True if get_environment() == "development" else False,
        description="Enable or disable debug mode.",
    )
    app_data: Path = Field(
        default_factory=lambda v: (
            user_data_dir()
            if get_environment() == "production"
            else application_root() / "data"
        ),
        description="""
        The application data directory. The default value is based on the environment.
        In development or testing, it points to a local 'data' directory.
        In production, it points to a hidden directory in the user's home.
        1. Development/Testing: ./data
        2. Production: ~/.wembed
        """,
    )

    logs_dir: Path = Field(
        default_factory=lambda v: (
            user_data_dir() / "logs"
            if get_environment() == "production"
            else application_root() / "data" / "logs"
        ),
        description="logs directory based on the application data directory",
    )

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
        if "USERNAME" in env:
            return env["USERNAME"]
        if "USER" in env:
            return env["USER"]
        return "user"

    sqlalchemy_uri: str = Field(
        default_factory=lambda: (
            f"sqlite:///{(Path().home() / '.wembed' / 'wembed.db').as_posix().replace('\\', '/')}"
            if get_environment() == "production"
            else (
                f"sqlite:///{(application_root() / 'data' / 'wembed.db').as_posix().replace('\\', '/')}"
                if not env.get("SQLALCHEMY_URI")
                else env["SQLALCHEMY_URI"].replace("\\", "/")
            )
        ),
        description="""
        The SQLAlchemy database URI.
        Defaults to a SQLite database in the application data directory if not set.
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

    def __init__(self, **data: Any):
        if get_environment() == "development":
            data["debug"] = True
        super().__init__(**data)
        self.ensure_paths()

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


__all__ = ["AppConfig", "GotifyConfig", "get_environment"]
