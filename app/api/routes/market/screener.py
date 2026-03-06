import json
from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings

router = APIRouter(prefix="/market/screener", tags=["Screener"])
eodhd = EodhdClient()

VALID_SORT_FIELDS = {
    "refund_1d_p",        # 1-day return % 
    "refund_1d_p.desc",   # top gainers
    "refund_1d_p.asc",    # top losers
    "avgvol_1d",          # most active
    "avgvol_200d",
    "market_capitalization",
    "market_capitalization.desc",
    "market_capitalization.asc",
    "adjusted_close",
    "dividend_yield",
}


@router.get("/")
async def get_screener(
    sort: str = Query(..., description="Sort field e.g. refund_1d_p.desc"),
    limit: int = Query(20, ge=1, le=100, description="Number of results, max 100"),
    filters: str = Query(
        "[]",
        description='JSON array of filter arrays e.g. [["exchange","=","US"],["market_capitalization",">","1000000000"]]'
    ),
):
    """
    Screen and sort stocks using custom filters.

    Returns a list of stocks matching the given filter criteria, sorted by the
    specified field. Filters are passed as a URL-encoded JSON array of condition
    tuples. Cached for 5 minutes.

    **Valid `sort` values:** `refund_1d_p`, `refund_1d_p.desc`, `refund_1d_p.asc`,
    `avgvol_1d`, `avgvol_200d`, `market_capitalization`, `market_capitalization.desc`,
    `market_capitalization.asc`, `adjusted_close`, `dividend_yield`

    **Filter format:** JSON array of `[field, operator, value]` tuples.
    Supported operators: `=`, `>`, `<`, `>=`, `<=`, `!=`

    Example: `[["exchange","=","US"],["market_capitalization",">","1000000000"]]`

    - **sort**: Sort field (required)
    - **limit**: Number of results to return, max 100 (default: 20)
    - **filters**: URL-encoded JSON filter array (default: no filters)
    """
    if sort not in VALID_SORT_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort field '{sort}'. Valid options are: {sorted(VALID_SORT_FIELDS)}"
        )

    # Parse and validate filters JSON
    try:
        parsed_filters = json.loads(filters)
        if not isinstance(parsed_filters, list):
            raise ValueError("filters must be a JSON array")
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid filters format: {str(e)}. Expected JSON array of arrays."
        )

    # Cache key based on exact query params
    cache_key = f"screener:{sort}:{limit}:{filters}"

    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        screener_data = await eodhd.get_screener_data(sort, limit, parsed_filters)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(cache_key, screener_data, settings.SCREENER_CACHE_TTL)
    return screener_data


@router.get("/gainers")
async def get_top_gainers(
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get the top gaining US stocks by 1-day return.

    Returns US-listed stocks sorted by 1-day return percentage in descending
    order. Equivalent to calling the screener with `sort=refund_1d_p.desc`
    and `filters=[["exchange","=","US"]]`. Cached for 5 minutes.

    - **limit**: Number of results to return, max 100 (default: 20)
    """
    cache_key = f"screener:gainers:{limit}"

    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        screener_data = await eodhd.get_screener_data(
            sort="refund_1d_p.desc",
            limit=limit,
            filters=[["exchange", "=", "US"]]
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(cache_key, screener_data, settings.SCREENER_CACHE_TTL)
    return screener_data


@router.get("/losers")
async def get_top_losers(
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get the top losing US stocks by 1-day return.

    Returns US-listed stocks sorted by 1-day return percentage in ascending
    order. Equivalent to calling the screener with `sort=refund_1d_p.asc`
    and `filters=[["exchange","=","US"]]`. Cached for 5 minutes.

    - **limit**: Number of results to return, max 100 (default: 20)
    """
    cache_key = f"screener:losers:{limit}"

    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        screener_data = await eodhd.get_screener_data(
            sort="refund_1d_p.asc",
            limit=limit,
            filters=[["exchange", "=", "US"]]
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(cache_key, screener_data, settings.SCREENER_CACHE_TTL)
    return screener_data


@router.get("/most-active")
async def get_most_active(
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get the most actively traded US stocks by 1-day volume.

    Returns US-listed stocks sorted by average 1-day trading volume in
    descending order. Equivalent to calling the screener with `sort=avgvol_1d.desc`
    and `filters=[["exchange","=","US"]]`. Cached for 5 minutes.

    - **limit**: Number of results to return, max 100 (default: 20)
    """
    cache_key = f"screener:most-active:{limit}"

    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        screener_data = await eodhd.get_screener_data(
            sort="avgvol_1d.desc",
            limit=limit,
            filters=[["exchange", "=", "US"]]
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(cache_key, screener_data, settings.SCREENER_CACHE_TTL)
    return screener_data