from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings


router = APIRouter(
    prefix="/stock",
    tags=["insider_trades"],
)

eodhd = EodhdClient()

@router.get("/insider_transactions")
async def get_insider_transactions_data(
    symbol: str | None = Query(None, description="Symbol of the stock (optional)"),
    limit: int | None = Query(None, description="The number of insider transactions to return"),
):
    sym = symbol.upper() if symbol else None
    cache_key = f"insider_trades:{sym or 'all'}:{limit or 'all'}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        insider_transactions_data = await eodhd.get_insider_transactions_data(symbol=sym, limit=limit)
        await cache.set_cache(cache_key, insider_transactions_data, settings.INSIDER_TRANSACTIONS_CACHE_TTL)
        return insider_transactions_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    
    