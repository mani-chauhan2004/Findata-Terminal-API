from fastapi import APIRouter, HTTPException
from app.services.sheets_client import sheets_client
from app.services.cache import cache

router = APIRouter(
    prefix="/market",
    tags=["Symbols"],
)

_CACHE_KEY = "market:symbols"
_CACHE_TTL = 86400  # 24h — sheet rarely changes


@router.get("/symbols")
async def get_symbols():
    """
    Returns the curated list of supported symbols with metadata
    (ticker, name, logo URL, Twitter, LinkedIn). Cached for 24 hours.
    """
    cached = await cache.get_cache(_CACHE_KEY)
    if cached is not None:
        return cached

    try:
        data = sheets_client.get_symbols()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(_CACHE_KEY, data, _CACHE_TTL)
    return data
