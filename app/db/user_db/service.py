from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import User
from sqlalchemy.exc import IntegrityError, OperationalError
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def test_db_connection(self):
        """Test if the database connection is working."""
        try:
            with self.db_manager.get_session() as session:
                # Attempt a simple query to check the connection
                stmt = select(User).limit(1)  # Query a small part of the User table
                session.execute(stmt)
            logger.info("Database connection is successful.")
            return True
        except OperationalError as e:
            logger.error("Database connection failed: %s", e)
            return False

    def get_user_by_username(self, username: str) -> User:
        """
        Retrieve a user by username.
        
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

    def update_user_game_stats(self, username: str, won: bool) -> None:
        """Update a user's game statistics synchronously"""
        with self.db_manager.get_session() as session:
            logger.info("Attempting to update stats for user %s", username)
            try:
                stmt = select(User).where(User.username == username)
                result = session.execute(stmt)
                user = result.scalar_one_or_none()

                if user:
                    user.update_game_stats(won)
                    session.commit()
                    logger.info("Successfully updated stats for user %s", username)
            except Exception as e:
                session.rollback()
                logger.error("Error updating stats for %s: %s", username, e)

    def create_or_get_user(self, username: str) -> int:
        """
        Retrieve or create a user by username.
        (This is here mostly to make the workflow easier before auth)
        
        Args:
            username (str)
        
        Returns:
            User.id (int)
        
        Raises:
            RuntimeError: 
        """
        logger.info('Fetching or creating user')
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