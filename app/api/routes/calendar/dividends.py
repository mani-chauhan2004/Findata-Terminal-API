from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings

router = APIRouter(prefix="/calendar/dividends", tags=["Dividend Calendar"])
eodhd = EodhdClient()


@router.get("/")
async def get_dividend_calendar(
    date: str = Query(..., description="Ex-dividend date YYYY-MM-DD"),
):
    """Get all stocks going ex-dividend on a specific date."""
    cache_key = f"calendar:dividends:{date}"

    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        dividend_calendar_data = await eodhd.get_dividend_calendar_data(date_eq=date)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(cache_key, dividend_calendar_data, settings.DIVIDEND_CALENDAR_CACHE_TTL)
    return dividend_calendar_data
