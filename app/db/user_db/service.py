from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import User
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def _get_user_by_username(self, username: str) -> User:

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
        with self.db_manager.get_session() as session:
            stmt = select(User).where(User.username == username)
            result = session.execute(stmt)
            return result.scalar_one_or_none()

    def _update_user_game_stats(self, username: str, won: bool) -> None:
        """Update a user's game statistics synchronously"""
        with self.db_manager.get_session() as session:
            try:
                stmt = select(User).where(User.username == username)
                result = session.execute(stmt)
                user = result.scalar_one_or_none()

                if user:
                    user.update_game_stats(won)
                    session.commit()
                    logger.info("Updated stats for user %s", username)
            except Exception as e:
                session.rollback()
                logger.error("Error updating user stats: %s", e)

    def create_or_get_user(self, username: str) -> int:
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
        with self.db_manager.get_session() as session:
            try:
                stmt = select(User).where(User.username == username)
                result = session.execute(stmt)
                user = result.scalar_one_or_none()

                if not user:
                    user = User(username=username)
                    session.add(user)
                    session.commit()
                    logger.info("Created new user: %s", username)
                else:
                    logger.info("Found existing user: %s", username)

                return user.id
            except Exception as e:
                session.rollback()
                logger.error("Error creating or retrieving user: %s", e)