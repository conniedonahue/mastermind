from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Optional
import logging

from .models import User, Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    Manages database connections and sessions.
    
    Args:
        database_url (str): Database connection URL
        
    Attributes:
        engine: SQLAlchemy engine instance
        SessionLocal: Session factory for creating new database sessions
    """

    def __init__(self, database_url: str):
        self.engine = create_engine(
            database_url,
            echo=True,
            pool_pre_ping=True, 
            pool_size=20,
            max_overflow=10
        )
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self):
        """
        Initializes database by creating all defined tables.
        
        Raises:
            SQLAlchemyError: If table creation fails
        """

        with self.engine.begin() as conn:
            Base.metadata.create_all(bind=conn)
            logger.info("Database tables created successfully")

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.
        
        Yields:
            Session: Database session
            
        Raises:
            Exception: Any exception during session use, ensures session closure
        """
        
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()