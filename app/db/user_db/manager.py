from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from typing import Optional
import logging
import asyncio
from .models import User, Base
from .service import UserService

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, database_url: str):
        """
        Initialize database manager with async engine and session factory
        
        Args:
            database_url (str): Database URL (should be async compatible, e.g., 
                              postgresql+asyncpg:// instead of postgresql://)
        """
        # Create async engine with echo for SQL logging
        self.engine = create_async_engine(
            database_url,
            echo=True,
            pool_size=20,
            max_overflow=10
        )
        
        # Create async session factory
        self.AsyncSessionLocal = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def init_db(self):
        """Initialize database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")

    async def get_session(self) -> AsyncSession:
        """Get a new async session"""
        return self.AsyncSessionLocal()