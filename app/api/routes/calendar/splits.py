from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings

router = APIRouter(prefix="/calendar/splits", tags=["Split Calendar"])
eodhd = EodhdClient()


@router.get("/")
async def get_split_calendar(
    from_date: str = Query(..., alias="from", description="Start date YYYY-MM-DD"),
    to_date: str = Query(..., alias="to", description="End date YYYY-MM-DD"),
):
    """
    Get the stock split calendar for a date range.

    Returns scheduled and historical stock splits within the given date range,
    including the split ratio (e.g. 4:1). Cached for 1 hour.

    - **from**: Start date in `YYYY-MM-DD` format (required)
    - **to**: End date in `YYYY-MM-DD` format (required)
    """
    cache_key = f"calendar:splits:{from_date}:{to_date}"

    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        split_calendar_data = await eodhd.get_split_calendar_data(from_date, to_date)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(cache_key, split_calendar_data, settings.SPLIT_CALENDAR_CACHE_TTL)
    return split_calendar_data