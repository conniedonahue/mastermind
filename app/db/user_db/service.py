from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import User
from sqlalchemy.exc import IntegrityError, OperationalError
import logging

logger = logging.getLogger(__name__)

class UserService:
    """
    Service for managing User Database operations and persistence.
    
    Args:
        db_manager (DatabaseManager): Database manager instance for database operations
    """

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def test_db_connection(self):
        """
        Tests if the database connection is working.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            OperationalError: If database connection fails
        """

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
            username (str): Username to search for
            
        Returns:
            User: User object if found, None otherwise
            
        Raises:
            OperationalError: If database operation fails
        """

        with self.db_manager.get_session() as session:
            stmt = select(User).where(User.username == username)
            result = session.execute(stmt)
            return result.scalar_one_or_none()

    def update_user_game_stats(self, username: str, won: bool) -> None:
        """
        Updates a user's game statistics synchronously.
        
        Args:
            username (str): Username of the player
            won (bool): Whether the game was won
            
        Raises:
            Exception: If update fails, with session rollback
        """

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
        Retrieves existing user or creates new user if not found.
        
        Args:
            username (str): Username to look up or create
            
        Returns:
            int: User ID
            
        Raises:
            Exception: If database operation fails, with session rollback
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