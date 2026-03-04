from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings


router = APIRouter(
    prefix="/stock",
    tags=["dividends"],
)

eodhd = EodhdClient()

@router.get("/{symbol}/dividends")
async def get_dividend_calendar_data(
    symbol: str,
    from_date: str = Query(..., alias="from", description="Start date in YYYY-MM-DD format"),
    to_date: str = Query(..., alias="to", description="End date in YYYY-MM-DD format"),
):
    sym = symbol.upper()
    cache_key = f"dividends:{sym}:{from_date}:{to_date}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        dividend_calendar_data = await eodhd.get_dividend_calendar_data(symbol=sym, from_date=from_date, to_date=to_date)
        await cache.set_cache(cache_key, dividend_calendar_data, settings.DIVIDEND_CALENDAR_CACHE_TTL)
        return dividend_calendar_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    

