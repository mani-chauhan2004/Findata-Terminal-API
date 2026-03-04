from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings

router = APIRouter(prefix="/calendar/economic", tags=["Economic Calendar"])
eodhd = EodhdClient()

# ISO 3166 country codes from your spreadsheet
VALID_COUNTRIES = {
    "US", "GB", "DE", "FR", "JP", "CN", "AU",
    "CA", "CH", "EU", "IN", "BR", "KR", "MX",
}


@router.get("/")
async def get_economic_calendar(
    from_date: str = Query(..., alias="from", description="Start date YYYY-MM-DD"),
    to_date: str = Query(..., alias="to", description="End date YYYY-MM-DD"),
    country: str | None = Query(None, description="ISO 3166 2-letter country code e.g. US, GB, DE"),
):
    if country and country.upper() not in VALID_COUNTRIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid country '{country}'. Valid options are: {sorted(VALID_COUNTRIES)}"
        )

    cache_key = f"calendar:economic:{from_date}:{to_date}:{country or 'all'}"

    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        economic_calendar_data = await eodhd.get_economic_events_data(from_date, to_date)

        # Filter by country client-side if provided
        # EODHD doesn't support country filter on this endpoint directly
        if country:
            economic_calendar_data = [
                event for event in economic_calendar_data
                if event.get("country", "").upper() == country.upper()
            ]

    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(cache_key, economic_calendar_data, settings.ECONOMIC_CALENDAR_CACHE_TTL)
    return economic_calendar_data