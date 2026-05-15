from fastapi import APIRouter, Depends, HTTPException
from app.core.dependencies import verify_admin_key
from app.services.cache import cache

router = APIRouter(
    prefix="/admin/cache",
    tags=["Admin"],
    dependencies=[Depends(verify_admin_key)],
)


@router.delete("/{cache_key:path}")
async def invalidate_cache(cache_key: str):
    """
    Invalidates a cache entry by key. The next request for that resource
    will fetch fresh data and repopulate the cache.

    Example keys:
    - `market:symbols`
    - `market:news:symbols`
    """
    await cache.invalidate_cache(cache_key)
    return {"detail": f"Cache key '{cache_key}' invalidated"}
