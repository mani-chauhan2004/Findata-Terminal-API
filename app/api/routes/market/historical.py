from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings
from typing import Literal


router = APIRouter(
    prefix="/market",
    tags=["Historical"],
)

eodhd = EodhdClient()


@router.get("/intraday")
async def get_intraday(
    symbol: str = Query(..., description="Symbol with exchange suffix (e.g. `ETH-USD.CC`, `AAPL.US`)"),
    interval: Literal["1m", "5m", "1h"] = Query("1h", description="Bar interval: `1m`, `5m`, or `1h`"),
    from_timestamp: int | None = Query(None, alias="from", description="Start time as Unix timestamp (UTC)"),
    to_timestamp: int | None = Query(None, alias="to", description="End time as Unix timestamp (UTC)"),
):
    """
    Get intraday OHLCV bars for any symbol.

    Returns an array of bars with `datetime`, `open`, `high`, `low`, `close`,
    and `volume` fields. When `from`/`to` are omitted the last 120 days are
    returned. Cached for 60 seconds.

    - **symbol**: Symbol with exchange suffix (e.g. `ETH-USD.CC`, `AAPL.US`)
    - **interval**: Bar size — `1m`, `5m` (default), or `1h`
    - **from**: Start as Unix timestamp in UTC (optional)
    - **to**: End as Unix timestamp in UTC (optional)
    """
    sym = symbol.upper()
    cache_key = f"intraday:{sym}:{interval}:{from_timestamp}:{to_timestamp}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        data = await eodhd.get_intraday_data(
            symbol=sym,
            interval=interval,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
        )
        await cache.set_cache(cache_key, data, settings.INTRADAY_CACHE_TTL)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/eod")
async def get_eod(
    symbol: str = Query(..., description="Symbol with exchange suffix (e.g. `ETH-USD.CC`, `AAPL.US`, `GC.COMM`)"),
    from_date: str | None = Query(None, alias="from", description="Start date in YYYY-MM-DD format (optional)"),
    to_date: str | None = Query(None, alias="to", description="End date in YYYY-MM-DD format (optional)"),
    period: Literal["d", "w", "m"] = Query("d", description="Bar period: `d` daily, `w` weekly, `m` monthly"),
):
    """
    Get end-of-day OHLCV bars for any symbol across any exchange type.

    Returns an array of bars with `date`, `open`, `high`, `low`, `close`,
    `adjusted_close`, and `volume` fields. When `from`/`to` are omitted the
    full available history is returned. Cached for 1 hour.

    - **symbol**: Symbol with exchange suffix (e.g. `ETH-USD.CC`, `AAPL.US`, `GSPC.INDX`)
    - **from**: Start date in `YYYY-MM-DD` format (optional)
    - **to**: End date in `YYYY-MM-DD` format (optional)
    - **period**: `d` daily (default), `w` weekly, `m` monthly
    """
    sym = symbol.upper()
    cache_key = f"eod:{sym}:{period}:{from_date}:{to_date}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        data = await eodhd.get_generic_eod_data(
            symbol=sym,
            from_date=from_date,
            to_date=to_date,
            period=period,
        )
        await cache.set_cache(cache_key, data, settings.GENERIC_EOD_CACHE_TTL)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
