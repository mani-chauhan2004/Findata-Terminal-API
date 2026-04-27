from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings


router = APIRouter(
    prefix="/market",
    tags=["Quotes"],
)

eodhd = EodhdClient()

SUPPORTED_EXCHANGES = ["US", "INDX", "COMM", "CC", "GBOND", "FOREX"]


@router.get("/real-time-quotes")
async def get_mixed_real_time_quotes(
    symbols: str = Query(
        ...,
        description=(
            "Comma-separated symbols with exchange suffixes "
            "(e.g. `TSLA.US,ETH-USD.CC,GC.COMM,GSPC.INDX`). "
            f"Supported exchanges: {', '.join(SUPPORTED_EXCHANGES)}"
        ),
    ),
):
    """
    Get real-time quotes for a mixed list of symbols across any exchange type.

    Accepts symbols with explicit exchange suffixes so you can fetch stocks,
    crypto, indices, and commodities in a single call. Pass one symbol to get
    a JSON object; pass multiple to get a JSON array. Cached for 15 seconds.

    - **symbols**: Comma-separated symbols with exchange suffix
      (e.g. `TSLA.US,ETH-USD.CC,GC.COMM,GSPC.INDX`)
    """
    syms = [s.strip().upper() for s in symbols.split(",")]
    cache_key = f"mixed_real_time_quotes:{','.join(sorted(syms))}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        data = await eodhd.get_mixed_real_time_quotes_data(symbols=syms)
        await cache.set_cache(cache_key, data, settings.MIXED_REAL_TIME_QUOTES_CACHE_TTL)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
