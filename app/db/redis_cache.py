import redis
import json
from typing import Any, Optional
from ..core.config import settings

class RedisCache:
    def __init__(self):
        self._redis_client = None
    
    @property
    def client(self) -> redis.Redis:
        if self._redis_client is None:
            self._redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True
            )
        return self._redis_client


    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache"""
        data = self.client.get(key)
        if data:
            return json.loads(str(data)) #could be problem with str
        return None


    def set(self, key: str, value: Any, ttl: Optional[int] = None) :
        """Set a value in the cache with optional ttl"""
        if ttl is None:
            ttl = settings.CACHE_TTL

        serialized = json.dumps(value)
        return self.client.setex(key, ttl, serialized)


    def  delete(self, key: str) -> bool:
        """Delete key from cache"""
        return bool(self.client.delete(key))


    def flush(self) -> bool:
        """Clear entire cache"""
        return bool(self.client.flushdb())

    def increment(self, key: str, amount: int = 1):
        """Increment a counter in redis"""
        return self.client.incrby(key, amount)


    def expire(self, key: str, ttl: int):
        """Set expiration for a key"""
        return self.client.expire(key, ttl)

cache = RedisCache()
