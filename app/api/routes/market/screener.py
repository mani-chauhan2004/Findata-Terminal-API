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
    """Shortcut — top gainers by 1-day return."""
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
    """Shortcut — top losers by 1-day return."""
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
    """Shortcut — most active by 1-day average volume."""
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