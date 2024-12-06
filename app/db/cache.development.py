from typing import Dict, Optional

class Cache:
    _store: Dict[str, dict] = {}

    @classmethod
    def create_session(cls, session_id: str, data: dict) -> None:
        cls._store[session_id] = data

    @classmethod
    def get_session(cls, session_id: str) -> Optional[dict]:
        return cls._store.get(session_id)

    @classmethod
    def update_session(cls, session_id: str, data: dict) -> None:
        if session_id in cls._store:
            cls._store[session_id].update(data)

    @classmethod
    def delete_session(cls, session_id: str) -> None:
        cls._store.pop(session_id, None)
