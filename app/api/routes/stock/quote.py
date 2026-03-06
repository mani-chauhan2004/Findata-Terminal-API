from fastapi import APIRouter, HTTPException
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings


router = APIRouter(
    prefix="/stock",
    tags=["quote"],
)

eodhd = EodhdClient()

@router.get("/{symbol}/quote")
async def get_realtime_quote(symbol: str):
    """
    Get a real-time quote for a stock.

    Returns the latest price, open, high, low, volume, and percentage change
    for the given ticker symbol. Cached for 15 seconds.

    - **symbol**: Stock ticker (e.g. `AAPL`, `TSLA`, `MSFT`)
    """
    sym = symbol.upper()
    cache_key = f"quote:realtime:{sym}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        quote_data = await eodhd.get_real_time_quote_data(sym)
        await cache.set_cache(cache_key, quote_data, settings.REALTIME_QUOTE_CACHE_TTL)
        return quote_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/{symbol}/quote/delayed")
async def get_us_quote_delayed(symbol: str):
    """
    Get a delayed (15-minute) quote for a US-listed stock.

    Returns the same fields as the real-time quote endpoint but with a
    15-minute delay. Available for US exchange securities only. Cached for 60 seconds.

    - **symbol**: US stock ticker (e.g. `AAPL`, `TSLA`)
    """
    sym = symbol.upper()
    cache_key = f"quote:delayed:{sym}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        quote_data = await eodhd.get_us_quote_delayed_data(sym)
        await cache.set_cache(cache_key, quote_data, settings.US_QUOTE_DELAYED_CACHE_TTL)
        return quote_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))