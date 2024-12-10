from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from typing import Optional
import logging
import asyncio
from contextlib import asynccontextmanager
from sqlalchemy.pool import QueuePool
from .models import User, Base
from .service import UserService

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            echo=True,
            pool_pre_ping=True,  # Verify connections before usage
            pool_size=20,
            max_overflow=10
        )
        
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

    @asynccontextmanager
    async def get_session(self) -> AsyncSession:
        """Get a new async session using context manager"""
        session = self.AsyncSessionLocal()
        try:
            yield session
        finally:
            await session.close()