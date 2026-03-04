from app.core.redis_client import get_redis
import json

class CacheService:
    async def get_cache(self, key: str) -> dict | None:
        redis = await get_redis()
        data = await redis.get(key)

        if data is not None:
            return json.loads(data)

        return None


    async def set_cache(self, key: str, data: dict, ttl: int) -> None:
        redis = await get_redis()
        await redis.set(key, json.dumps(data), ex=ttl)


    async def invalidate_cache(self, key: str) -> None:
        redis = await get_redis()
        await redis.delete(key)


cache = CacheService()