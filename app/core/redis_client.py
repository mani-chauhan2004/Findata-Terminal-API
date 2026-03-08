import redis.asyncio as redis
from app.core.config import settings

_redis: redis.Redis | None = None

async def get_redis() -> redis.Redis:
    global _redis
    if _redis is None:
        _redis = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None