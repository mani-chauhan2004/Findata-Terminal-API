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
    """
    Get the earnings release calendar for a date range.

    Returns a list of companies scheduled to report earnings within the given
    date range, including estimated and actual EPS where available. Cached for 1 hour.

    - **from**: Start date in `YYYY-MM-DD` format (required)
    - **to**: End date in `YYYY-MM-DD` format (required)
    """
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
    """
    Get earnings dates for a specific company.

    Returns historical and upcoming earnings report dates along with EPS
    estimates and actuals for the given ticker symbol. Cached for 1 hour.

    - **symbol**: Stock ticker (e.g. `AAPL`, `MSFT`)
    """
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