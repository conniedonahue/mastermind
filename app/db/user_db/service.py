from sqlalchemy.orm import Session
from .models import User
from sqlalchemy.exc import IntegrityError
import asyncio
import logging

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, username: str, email: str, password: str) -> User:
        """
        Create a new user in the database
        
        Args:
            username (str): Chosen username
            email (str): User's email
            password (str): User's password
        
        Returns:
            User: Created user instance
        
        Raises:
            ValueError: If username or email already exists
        """
        try:
            user = User.create_user(username, email, password)
            self.session.add(user)
            self.session.commit()
            return user
        except IntegrityError:
            self.session.rollback()
            raise ValueError("Username or email already exists")

    def get_user_by_username(self, username: str) -> User:
        """
        Retrieve a user by username
        
        Args:
            username (str): Username to search for
        
        Returns:
            User: User instance or None
        """
        return self.session.query(User).filter_by(username=username).first()

    def authenticate_user(self, username: str, password: str) -> User:
        """
        Authenticate a user
        
        Args:
            username (str): User's username
            password (str): Provided password
        
        Returns:
            User: Authenticated user
        
        Raises:
            ValueError: If authentication fails
        """
        user = self.get_user_by_username(username)
        if not user or not user.verify_password(password):
            raise ValueError("Invalid username or password")
        return user

    async def update_user_game_stats(self, username: str, won: bool):
        """
        Update a user's game statistics
        
        Args:
            username (str): Username
            won (bool): Whether the game was won
        """
        try: 
            user = self.get_user_by_username(username)
            if user:
                user.update_game_stats(won)
                await self.session.commit()
        except:
            await self.session.rollback()
            logger.error(f"Error updating user stats: {e}")