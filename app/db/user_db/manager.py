from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from typing import Optional
import logging

from .models import User, Base

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, database_url: str):
        # Use the synchronous engine and sessionmaker
        self.engine = create_engine(
            database_url,
            echo=True,
            pool_pre_ping=True, 
            pool_size=20,
            max_overflow=10
        )
        self.SessionLocal = sessionmaker(bind=self.engine)



    def init_db(self):
        """Initialize database tables"""
        # Use synchronous connection to create tables
        with self.engine.begin() as conn:
            Base.metadata.create_all(bind=conn)
            logger.info("Database tables created successfully")

    @contextmanager
    def get_session(self):
        """Get a new synchronous session using context manager"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()