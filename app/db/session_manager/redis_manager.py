from redis import Redis
from typing import Optional
from datetime import timedelta
from . import SessionManagerInterface
import json
import uuid

import logging

logger = logging.getLogger(__name__)

class RedisSessionManager(SessionManagerInterface):
    """Redis-based session management (for production)."""

    def __init__(self, redis_client: Redis, session_timeout: timedelta = timedelta(hours=1)):
        self.redis_client = redis_client
        self.session_timeout = session_timeout

    def create_session(self, data: dict) -> str:
        session_id = str(uuid.uuid4())
        self.redis_client.setex(
            session_id,
            self.session_timeout,
            json.dumps(data)
        )
        return session_id

    def get_session(self, session_id: str) -> Optional[dict]:
        session_data = self.redis_client.get(session_id)
        if not session_data:
            logger.warning("Session not found: %s", session_id)
            return None
        return json.loads(session_data)

    def update_session(self, session_id: str, updates: dict) -> bool:
        logger.warning("in update")
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
        self.redis_client.delete(session_id)
