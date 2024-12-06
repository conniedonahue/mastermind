# db/cache.py

# import redis
# import json

# class Cache:
#     _client = redis.StrictRedis(host='localhost', port=6379, db=0)

#     @classmethod
#     def create_session(cls, session_id: str, data: dict) -> None:
#         cls._client.set(session_id, json.dumps(data))

#     @classmethod
#     def get_session(cls, session_id: str) -> Optional[dict]:
#         session_data = cls._client.get(session_id)
#         return json.loads(session_data) if session_data else None

#     @classmethod
#     def update_session(cls, session_id: str, data: dict) -> None:
#         existing_data = cls.get_session(session_id) or {}
#         existing_data.update(data)
#         cls.create_session(session_id, existing_data)

#     @classmethod
#     def delete_session(cls, session_id: str) -> None:
#         cls._client.delete(session_id)
