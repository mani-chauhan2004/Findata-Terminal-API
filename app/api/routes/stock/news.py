from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings


router = APIRouter(
    prefix="/stock",
    tags=["news"],
)

eodhd = EodhdClient()

@router.get("/{symbol}/news")
async def get_news_data(
    symbol: str,
    limit: int | None = Query(None, ge=1, le=1000, description="The number of news items to return"),
):
    sym = symbol.upper()
    cache_key = f"news:{sym}:{limit or 'all'}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        news_data = await eodhd.get_news_data(symbol=sym, limit=limit)
        await cache.set_cache(cache_key, news_data, settings.NEWS_CACHE_TTL)
        return news_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    
    