import json
import redis

from app.config import settings


class RedisMemoryService:

    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )

    def add_message(self, session_id: str, role: str, content: str):
        key = f"chat_history:{session_id}"

        message = {
            "role": role,
            "content": content
        }

        self.redis.rpush(key, json.dumps(message))

    def get_history(self, session_id: str, limit: int = 10):
        key = f"chat_history:{session_id}"

        messages = self.redis.lrange(key, -limit, -1)

        return [json.loads(message) for message in messages]


memory_service = RedisMemoryService()