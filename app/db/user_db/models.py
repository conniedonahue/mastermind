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
    email = Column(String(120), unique=True, nullable=False)
    
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(32), nullable=False)
    
    # Game statistics
    games_won = Column(Integer, default=0)
    games_lost = Column(Integer, default=0)
    total_games_played = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    @classmethod
    def create_user(cls, username, email, password):
        """
        Create a new user with secure password hashing
        
        Args:
            username (str): User's chosen username
            email (str): User's email address
            password (str): User's password
        
        Returns:
            User: New User instance
        """
        # Generate a secure salt
        salt = secrets.token_hex(16)  # 32 character salt
        password_hash = cls.hash_password(password, salt)
        
        return cls(
            username=username,
            email=email,
            password_hash=password_hash,
            salt=salt,
            games_won=0,
            games_lost=0,
            total_games_played=0
        )

    @staticmethod
    def hash_password(password, salt):
        """
        Securely hash the password using PBKDF2
        
        Args:
            password (str): Plain text password
            salt (str): Unique salt for the user
        
        Returns:
            str: Hashed password
        """
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000,
            dklen=32
        ).hex()

    def verify_password(self, provided_password):
        """
        Verify if the provided password is correct
        
        Args:
            provided_password (str): Password to verify
        
        Returns:
            bool: True if password is correct, False otherwise
        """
        # Recreate the hash with the stored salt
        hashed_password = self.hash_password(provided_password, self.salt)
        return hashed_password == self.password_hash

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