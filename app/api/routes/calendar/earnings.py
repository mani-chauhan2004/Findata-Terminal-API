from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings

router = APIRouter(prefix="/calendar/earnings", tags=["Earnings Calendar"])
eodhd = EodhdClient()


@router.get("/")
async def get_earnings_calendar(
    from_date: str = Query(..., alias="from", description="Start date YYYY-MM-DD"),
    to_date: str = Query(..., alias="to", description="End date YYYY-MM-DD"),
):
    cache_key = f"calendar:earnings:{from_date}:{to_date}"

    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        earnings_calendar_data = await eodhd.get_earnings_calendar_data(from_date=from_date, to_date=to_date)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(cache_key, earnings_calendar_data, settings.EARNINGS_CALENDAR_CACHE_TTL)
    return earnings_calendar_data


@router.get("/symbol/{symbol}")
async def get_earnings_calendar_by_symbol(symbol: str):
    """Get earnings calendar for a specific symbol."""
    sym = symbol.upper()
    cache_key = f"calendar:earnings:symbol:{sym}"

    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        earnings_calendar_data = await eodhd.get_earnings_calendar_data(sym)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(cache_key, earnings_calendar_data, settings.EARNINGS_CALENDAR_CACHE_TTL)
    return earnings_calendar_data