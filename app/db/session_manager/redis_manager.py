from redis import Redis
from typing import Optional
from datetime import timedelta
from . import SessionManagerInterface
import json
import uuid

import logging

logger = logging.getLogger(__name__)

class RedisSessionManager(SessionManagerInterface):
    """
    Redis-based session management implementation for production use.
    
    Args:
        redis_client (Redis): Initialized Redis client instance
        session_timeout (timedelta, optional): Time until session expiry. Defaults to 1 hour.
    """

    def __init__(self, redis_client: Redis, session_timeout: timedelta = timedelta(hours=1)):
        self.redis_client = redis_client
        self.session_timeout = session_timeout

    def create_session(self, data: dict) -> str:
        """
        Creates a new session in Redis.
        
        Args:
            data (dict): Session data to store
            
        Returns:
            str: Generated session ID
        """

        session_id = str(uuid.uuid4())
        self.redis_client.setex(
            session_id,
            self.session_timeout,
            json.dumps(data)
        )
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        """
        Retrieves session data from Redis.
        
        Args:
            session_id (str): Session identifier
            
        Returns:
            Optional[dict]: Session data if found, None otherwise
        """

        session_data = self.redis_client.get(session_id)
        if not session_data:
            logger.warning("Session not found: %s", session_id)
            return None
        return json.loads(session_data)

    def update_session(self, session_id: str, updates: dict) -> bool:
        """
        Updates an existing session in Redis.
        
        Args:
            session_id (str): Session identifier
            updates (dict): New data to update in the session
            
        Returns:
            bool: True if update successful, False if session not found
        """

        session_data = self.get_session(session_id)
        if not session_data:
            logger.warning("Session not found: %s", session_id)
            return False

        session_data.update(updates)
        self.redis_client.setex(
            session_id,
            self.session_timeout,
            json.dumps(session_data)
        )
        return True

    def delete_session(self, session_id: str) -> None:
        """
        Deletes a session from Redis.
        
        Args:
            session_id (str): Session identifier to delete
        """
        
        self.redis_client.delete(session_id)
