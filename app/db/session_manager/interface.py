from abc import ABC, abstractmethod
from typing import Dict, Optional

class SessionManagerInterface(ABC):
    """ Abstract base Session Manager class """

    @abstractmethod
    def create_session(self, data: dict) -> str:
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    def update_session(self, session_id: str, updates: dict) -> bool:
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> str:
        pass