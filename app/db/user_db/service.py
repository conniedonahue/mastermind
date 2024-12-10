from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import User
from sqlalchemy.exc import IntegrityError
import asyncio
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    async def _get_user_by_username(self, username: str) -> User:

        """
        Retrieve a user by username. If the user doesn't exist, it creates one
        (This is here mostly to make the workflow easier before auth)
        
        Args:
            username (str)
        
        Returns:
            User (User)
        
        Raises:
            RuntimeError: If unable to establish a connection to Redis
        """
        async with self.db_manager.get_session() as session:
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def _update_user_game_stats(self, username: str, won: bool) -> None:
        """
        Update a user's game statistics
        
        """
        async with self.db_manager.get_session() as session:
            async with session.begin():
                try:
                    stmt = select(User).where(User.username == username)
                    result = await session.execute(stmt)
                    user = result.scalar_one_or_none()
                    
                    if user:
                        user.update_game_stats(won)
                        await session.commit()
                        logger.info("Updated stats for user %s", username)
                except Exception as e:
                    await session.rollback()
                    logger.error("Error updating user stats: %s", e)

    async def _create_or_get_user(self, username: str) -> int:
        """
        Retrieve or create a user by username.
        (This is here mostly to make the workflow easier before auth)
        
        Args:
            username (str)
        
        Returns:
            User.id (int)
        
        Raises:
            RuntimeError: If unable to establish a connection to Redis
        """
        async with self.db_manager.get_session() as session:
            async with session.begin():
                stmt = select(User).where(User.username == username)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                
                if not user:
                    user = User(username=username)
                    session.add(user)
                    await session.commit()
                    logger.info("Created new user: %s", username)
                else:
                    logger.info("Found existing user: %s", username)
                
                return user.id

    # Synchronous wrappers made with asyncio.run() 
    def create_or_get_user(self, username: str) -> int:
        """Synchronous wrapper for create_or_get"""
        return asyncio.run(self._create_or_get_user(username))

    def update_user_game_stats(self, username: str, won: bool):
        """Synchronous wrapper for update_user_game_stats"""
        asyncio.run(self._update_user_game_stats(username, won))