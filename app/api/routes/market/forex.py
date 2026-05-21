from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings

router = APIRouter(prefix="/market/forex", tags=["Forex"])
eodhd = EodhdClient()

VALID_FOREX = {
    "EURUSD": "EUR/USD",
    "USDJPY": "US Dollar/Japanese Yen FX Spot Rate",
    "GBPUSD": "UK Pound Sterling/US Dollar FX Spot Rate",
    "USDCNY": "US Dollar/Chinese Renminbi FX Spot Rate",
    "USDINR": "US Dollar/Indian Rupee FX Spot Rate",
    "BRLUSD": "Brazilian Real/US Dollar FX Cross Rate",
    "CADUSD": "Canadian Dollar/US Dollar FX Cross Rate",
    "AUDUSD": "Australian Dollar/US Dollar FX Spot Rate",
    "USDKRW": "US Dollar/Korean Won FX Spot Rate",
    "USDMXN": "US Dollar/Mexican Peso FX Spot Rate",
}


@router.get("/real-time-quotes")
async def get_forex_real_time_quotes(
    symbols: str = Query(
        ...,
        description=(
            "Comma-separated forex pair symbols (e.g. `EURUSD` or `EURUSD,USDJPY`). "
            f"Supported pairs: {', '.join(VALID_FOREX)}"
        ),
    ),
):
    """
    Get real-time quotes for one or more USD forex pairs.

    Pass a single symbol to get a JSON object, or multiple comma-separated
    symbols to get a JSON array.
    Use `GET /market/forex` to retrieve the list of valid forex symbols.
    Cached for 15 seconds.

    - **symbols**: One or more forex pair symbols (e.g. `EURUSD` or `EURUSD,GBPUSD`)
    """
    syms = [s.strip().upper() for s in symbols.split(",")]
    invalid = [s for s in syms if s not in VALID_FOREX]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Unsupported forex symbols: {', '.join(invalid)}")

    cache_key = f"forex_real_time_quotes:{','.join(sorted(syms))}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        data = await eodhd.get_forex_real_time_quotes_data(symbols=syms)
        await cache.set_cache(cache_key, data, settings.FOREX_REAL_TIME_QUOTES_CACHE_TTL)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/")
async def list_forex():
    """
    List all supported USD forex pairs.

    Returns the full catalogue of forex pairs available in this API.
    Use the `symbol` field from this response as the `symbols` query parameter
    in the real-time-quotes endpoint.
    """
    return [
        {"symbol": symbol, "name": name}
        for symbol, name in VALID_FOREX.items()
    ]
