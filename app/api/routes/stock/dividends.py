from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings


router = APIRouter(
    prefix="/stock",
    tags=["dividends"],
)

eodhd = EodhdClient()

@router.get("/dividends")
async def get_dividend_calendar_data(
    symbol: str | None = Query(None, description="Symbol of the stock (optional)"),
    date_eq: str | None = Query(None, description="Date in YYYY-MM-DD format (optional)"),
    from_date: str | None = Query(None, alias="from", description="Start date in YYYY-MM-DD format"),
    to_date: str | None = Query(None, alias="to", description="End date in YYYY-MM-DD format"),
):
    if symbol is None and date_eq is None:
        raise HTTPException(status_code=400, detail="Either symbol or date_eq must be provided")
    sym = symbol.upper() if symbol else None
    cache_key = f"dividends:{sym or 'all'}:{date_eq or 'all'}:{from_date or 'all'}:{to_date or 'all'}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        dividend_calendar_data = await eodhd.get_dividend_calendar_data(symbol=sym, from_date=from_date, to_date=to_date, date_eq=date_eq)
        await cache.set_cache(cache_key, dividend_calendar_data, settings.DIVIDEND_CALENDAR_CACHE_TTL)
        return dividend_calendar_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    

