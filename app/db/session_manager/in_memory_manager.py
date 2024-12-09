from typing import Dict, Optional
from datetime import datetime, timedelta
from . import SessionManagerInterface
import uuid
import logging

logger = logging.getLogger(__name__)

class InMemorySessionManager(SessionManagerInterface):

    _store: Dict[str, Dict] = {}
    SESSION_TIMEOUT = timedelta(hours=1)  # TTL = 1 hour

    @classmethod
    def create_session(cls, data: dict) -> str:
        """
        Creates a session with automatic session_id and timestamp generation
        
        Args:
            data (dict): Initial session data
        
        Returns:
            str: Generated session ID
        """
        session_id = str(uuid.uuid4())
        session_data = {
            'id': session_id,
            'created_at': datetime.now(),
            'last_accessed': datetime.now(),
            'data': data,
            'status': 'active'
        }
        logger.info("Creating session: %s", session_id)
        cls._store[session_id] = session_data
        logger.debug("Session created: %s with initial data: %s", session_id, session_data)

        return session_id

    @classmethod
    def get_session(cls, session_id: str) -> Optional[dict]:
        """
        Retrieve a session, with automatic expiration check
        
        Args:
            session_id (str): Session identifier
        
        Returns:
            Optional[dict]: Session data or None if expired/not found
        """
        session = cls._store.get(session_id)
        
        if not session:
            logger.warning("Session not found: %s", session_id)
            return None
        
        # Check session expiration
        if datetime.now() - session['created_at'] > cls.SESSION_TIMEOUT:
            logger.info("Session expired: %s", session_id)
            cls.delete_session(session_id)
            return None
        
        # Update last accessed timestamp
        session['last_accessed'] = datetime.now()
        logger.debug("Session accessed: %s", session_id)
        return session['data']

    @classmethod
    def update_session(cls, session_id: str, updates: dict) -> bool:
        """
        Update an existing session
        
        Args:
            session_id (str): Session identifier
            updates (dict): Updates to apply to session
        
        Returns:
            bool: Whether update was successful
        """
        session = cls._store.get(session_id)
        if not session:
            logger.warning("Session not found for update: %s", session_id)
            return False
        
        session['data'].update(updates)
        session['last_accessed'] = datetime.now()
        logger.info("Session updated: %s with data: %s", session_id, updates)
        return True

    @classmethod
    def delete_session(cls, session_id: str) -> str:
        """
        Remove a session
        
        Args:
            session_id (str): Session identifier to remove
        """
        session_id = cls._store.pop(session_id, None)
        if session_id:
            logger.info("Deleted session: %s", session_id)
        else:
            logger.warning("Attempted to delete non-existing session: %s", session_id)
        return f"Deleted session ${session_id}"

    @classmethod
    def cleanup_expired_sessions(cls) -> int:
        """
        Remove all expired sessions
        
        Returns:
            int: Number of sessions cleaned up
        """
        now = datetime.now()
        expired_sessions = [
            session_id for session_id, session in cls._store.items()
            if now - session['created_at'] > cls.SESSION_TIMEOUT
        ]
        
        for session_id in expired_sessions:
            del cls._store[session_id]
        
        logger.info("Cleaned up %d expired sessions", len(expired_sessions))
        return len(expired_sessions)

    @classmethod
    def get_active_session_count(cls) -> int:
        """
        Get the number of active sessions
        
        Returns:
            int: Number of active sessions
        """
        now = datetime.now()

        active_sessions = 0
        
        for session in cls._store.values():
            if now - session['created_at'] <= cls.SESSION_TIMEOUT:
                active_sessions += 1
       
        logger.debug("Active session count: %d", active_sessions)

        return active_sessions