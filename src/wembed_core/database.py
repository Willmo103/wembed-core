from sqlalchemy.orm import declarative_base

from .config import AppConfig

AppBase = declarative_base()


class DatabaseService:
    _is_initialized = False

    def __init__(self, config: AppConfig):
        self.uri = str(config.sqlalchemy_uri)
        self.debug = config.environment == "development"
        self.engine = None
        self.SessionLocal = None

    def init_db(self):
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

    def get_db(self):
        if self.SessionLocal is None:
            raise Exception("Database not initialized. Call init_db() first.")
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
