from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings


router = APIRouter(
    prefix="/market/bonds",
    tags=["Bonds"],
)

eodhd = EodhdClient()

VALID_BONDS = {
    "US1Y":  "US 1-Year Treasury",
    "US2Y":  "US 2-Year Treasury",
    "US5Y":  "US 5-Year Treasury",
    "US10Y": "US 10-Year Treasury",
    "US30Y": "US 30-Year Treasury",
}


@router.get("/{bond}/historical-eod")
async def get_bond_historical_eod_data(
    bond: str,
    from_date: str | None = Query(None, alias="from", description="Start date in YYYY-MM-DD format (optional, defaults to full available history)"),
    to_date: str | None = Query(None, alias="to", description="End date in YYYY-MM-DD format (optional, defaults to latest available)"),
):
    """
    Get end-of-day (EOD) historical data for a government bond.

    Returns daily OHLCV records for the specified bond. Date range is optional —
    omitting both returns the full available history (5+ years). Use
    `GET /market/bonds` to retrieve the list of valid bond symbols. Cached for 1 hour.

    - **bond**: Bond symbol (e.g. `US2Y`, `US10Y`)
    - **from**: Start date in `YYYY-MM-DD` format (optional)
    - **to**: End date in `YYYY-MM-DD` format (optional)
    """
    bond = bond.upper()
    cache_key = f"bond_historical_eod:{bond}:{from_date}:{to_date}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        bond_historical_eod_data = await eodhd.get_bond_historical_eod_data(bond=bond, from_date=from_date, to_date=to_date)
        await cache.set_cache(cache_key, bond_historical_eod_data, settings.BOND_HISTORICAL_EOD_CACHE_TTL)
        return bond_historical_eod_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/")
async def list_bonds():
    """
    List all supported government bonds.

    Returns the full catalogue of bonds available in this API.
    Use the `symbol` field from this response as the `bond` path parameter
    in other bond endpoints.
    """
    return [
        {"symbol": symbol, "name": name}
        for symbol, name in VALID_BONDS.items()
    ]
