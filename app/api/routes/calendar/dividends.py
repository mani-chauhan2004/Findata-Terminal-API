from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings

router = APIRouter(prefix="/calendar/dividends", tags=["Dividend Calendar"])
eodhd = EodhdClient()


@router.get("/")
async def get_dividend_calendar(
    from_date: str = Query(..., alias="from", description="Start date YYYY-MM-DD"),
    to_date: str = Query(..., alias="to", description="End date YYYY-MM-DD"),
):
    cache_key = f"calendar:dividends:{from_date}:{to_date}"

    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        dividend_calendar_data = await eodhd.get_dividend_calendar_data(from_date, to_date)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(cache_key, dividend_calendar_data, settings.DIVIDEND_CALENDAR_CACHE_TTL)
    return dividend_calendar_data