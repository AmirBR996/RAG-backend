import redis
import json
from typing import List, Dict
from app.config import settings

class RedisMemoryService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT, 
            decode_responses=True
        )

    def add_message(self, session_id: str, role: str, content: str):
        key = f"chat_history:{session_id}"
        message = json.dumps({"role": role, "content": content})
        self.redis_client.rpush(key, message)

    def get_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        key = f"chat_history:{session_id}"
        raw_messages = self.redis_client.lrange(key, -limit, -1)
        return [json.loads(msg) for msg in raw_messages]

memory_service = RedisMemoryService()