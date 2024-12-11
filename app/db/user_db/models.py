from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .base import Base
import hashlib
import os
import secrets

class User(Base):
    """
    User model representing game players.
    
    Attributes:
        id (int): Primary key
        username (str): Unique username
        games_won (int): Number of games won
        games_lost (int): Number of games lost
        total_games_played (int): Total number of games played
        created_at (DateTime): Account creation timestamp
    """
    
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
   
    
    # Game statistics
    games_won = Column(Integer, default=0)
    games_lost = Column(Integer, default=0)
    total_games_played = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @classmethod
    def create_user(cls, username):
        """
        Create a new user
        
        Args:
            username (str): User's chosen username
            
        Returns:
            User: New User instance with default game statistics
        """

        return cls(
            username=username,
            games_won=0,
            games_lost=0,
            total_games_played=0
        )

    def update_game_stats(self, won=False):
        """
        Updates user's game statistics after a game.
        
        Args:
            won (bool, optional): Whether the game was won. Defaults to False.
        """

        self.total_games_played += 1
        if won:
            self.games_won += 1
        else:
            self.games_lost += 1