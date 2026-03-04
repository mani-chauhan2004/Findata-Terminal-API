from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings

router = APIRouter(prefix="/market/news", tags=["Market News"])
eodhd = EodhdClient()


@router.get("/")
async def get_market_news(
    limit: int = Query(50, ge=1, le=100, description="Number of news items to return")
):
    """General market news — no symbol filter."""
    cache_key = f"market:news:{limit}"

    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        market_news_data = await eodhd.get_news_data(symbol=None, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(cache_key, market_news_data, settings.NEWS_CACHE_TTL)
    return market_news_data