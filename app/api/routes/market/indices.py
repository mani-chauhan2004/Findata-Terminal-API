from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings


router = APIRouter(
    prefix="/market/indices",
    tags=["Indices"],
)

eodhd = EodhdClient()

VALID_INDICES = {
    # US
    "GSPC":  "S&P 500",
    "DJI":   "Dow Jones",
    "IXIC":  "Nasdaq Composite",
    "RUT":   "Russell 2000",
    # Europe
    "FTSE":  "FTSE 100",
    "GDAXI": "DAX",
    "FCHI":  "CAC 40",
    "STOXX50E": "Euro Stoxx 50",
    # Asia
    "N225":  "Nikkei 225",
    "HSI":   "Hang Seng",
    "000001": "Shanghai Composite",
}

@router.get("/{index}/real-time-quotes")
async def get_index_based_real_time_quotes_data(
    index: str,
):
    """
    Get a real-time quote for a market index.

    Returns the latest price, change, and volume data for the specified index.
    Use `GET /market/indices` to retrieve the list of valid index symbols.
    Cached for 30 seconds.

    - **index**: Index symbol (e.g. `GSPC` for S&P 500, `DJI` for Dow Jones)
    """
    index = index.upper()
    cache_key = f"index_based_real_time_quotes:{index}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        index_based_real_time_quotes_data = await eodhd.get_index_based_real_time_quotes_data(index=index)
        await cache.set_cache(cache_key, index_based_real_time_quotes_data, settings.INDEX_BASED_REAL_TIME_QUOTES_CACHE_TTL)
        return index_based_real_time_quotes_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/{index}/historical-eod")
async def get_index_based_historical_eod_data(
    index: str,
    from_date: str = Query(..., alias="from", description="Start date in YYYY-MM-DD format"),
    to_date: str = Query(..., alias="to", description="End date in YYYY-MM-DD format"),
):
    """
    Get end-of-day (EOD) historical data for a market index.

    Returns daily OHLCV records for the specified index over the given date
    range. Use `GET /market/indices` to retrieve the list of valid index
    symbols. Cached for 1 hour.

    - **index**: Index symbol (e.g. `GSPC`, `N225`)
    - **from**: Start date in `YYYY-MM-DD` format (required)
    - **to**: End date in `YYYY-MM-DD` format (required)
    """
    index = index.upper()
    cache_key = f"index_based_historical_eod:{index}:{from_date}:{to_date}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        index_based_historical_eod_data = await eodhd.get_index_based_historical_eod_data(index=index, from_date=from_date, to_date=to_date)
        await cache.set_cache(cache_key, index_based_historical_eod_data, settings.INDEX_BASED_HISTORICAL_EOD_CACHE_TTL)
        return index_based_historical_eod_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/")
async def list_indices():
    """
    List all supported market indices.

    Returns the full catalogue of indices available in this API, including US,
    European, and Asian markets. Use the `symbol` field from this response as
    the `index` path parameter in other index endpoints.
    """
    return [
        {"symbol": symbol, "name": name}
        for symbol, name in VALID_INDICES.items()
    ]