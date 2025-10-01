"""
SQLAlchemy setup and database service for the application.
"""
from typing import Generator

from sqlalchemy.orm import declarative_base, Session

from .config import AppConfig

AppBase = declarative_base()
"""
Declarative base for SQLAlchemy models.
"""


class DatabaseService:
    """
    Service class to manage database connections and sessions using SQLAlchemy.

    Methods:
        init_db(): Initializes the database connection and creates tables.
        get_db(): Provides a database session for use in application code.
    """
    _is_initialized = False

    def __init__(self, config: AppConfig):
        """
        Initialize the DatabaseService with the given configuration.
        Args:
            config (AppConfig): Application configuration containing database settings.
        """
        self.uri = str(config.sqlalchemy_uri)
        self.debug = config.environment == "development"
        self.engine = None
        self.SessionLocal = None

    def init_db(self) -> None:
        """
        Initialize the database connection and create tables if they do not exist.
        This method should be called once during application startup.
        """
        if self._is_initialized:
            return
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        self.engine = create_engine(self.uri, echo=self.debug)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        AppBase.metadata.create_all(bind=self.engine)
        self._is_initialized = True

    def get_db(self) -> "Generator[Session, None, None]":
        """
        Provide a database session for use in application code.
        Yields:
            Generator[Session, None, None]: A generator yielding a SQLAlchemy session.
        Raises:
            Exception: If the database has not been initialized.
        """
        if self.SessionLocal is None:
            raise Exception("Database not initialized. Call init_db() first.")
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
