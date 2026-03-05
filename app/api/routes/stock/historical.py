from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings


router = APIRouter(
    prefix="/stock",
    tags=["historical"],
)

eodhd = EodhdClient()

@router.get("/{symbol}/historical")
async def get_historical_eod_data(
    symbol: str, 
    from_date: str | None = Query(None, alias="from", description="Start date in YYYY-MM-DD format"),
    to_date: str | None = Query(None, alias="to", description="End date in YYYY-MM-DD format"),
):
    sym = symbol.upper()
    cache_key = f"historical:{sym}:{from_date}:{to_date}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        historical_data = await eodhd.get_hisorical_eod_data(symbol=sym, from_date=from_date, to_date=to_date)
        await cache.set_cache(cache_key, historical_data, settings.HISTORICAL_EOD_CACHE_TTL)
        return historical_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))




