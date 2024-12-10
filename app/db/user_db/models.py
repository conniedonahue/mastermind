from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .base import Base
import hashlib
import os
import secrets

class User(Base):
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
            User: New User instance
        """

        
        return cls(
            username=username,
            games_won=0,
            games_lost=0,
            total_games_played=0
        )

    def update_game_stats(self, won=False):
        """
        Update user's game statistics
        
        Args:
            won (bool): Whether the game was won
        """
        self.total_games_played += 1
        if won:
            self.games_won += 1
        else:
            self.games_lost += 1