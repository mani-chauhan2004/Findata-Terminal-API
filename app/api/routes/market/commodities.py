from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings

router = APIRouter(prefix="/market/commodities", tags=["Commodities"])
eodhd = EodhdClient()

VALID_COMMODITIES = {
    # Metals
    "GC":  "Gold",
    "SI":  "Silver",
    "PL":  "Platinum",
    "PA":  "Palladium",
    "HG":  "Copper",
    # Energy
    "CL":  "Crude Oil (WTI)",
    "BZ":  "Crude Oil (Brent)",
    "NG":  "Natural Gas",
    "HO":  "Heating Oil",
    "RB":  "Gasoline",
    # Agriculture
    "ZW":  "Wheat",
    "ZC":  "Corn",
    "ZS":  "Soybeans",
    "KC":  "Coffee",
    "SB":  "Sugar",
    "CC":  "Cocoa",
    "CT":  "Cotton",
}

@router.get("/real-time-quotes")
async def get_commodity_based_real_time_quotes_data(
    symbols: str = Query(..., description="Comma-separated commodity symbols (e.g. `GC` or `GC,SI,CL`)"),
):
    """
    Get real-time quotes for one or more commodities.

    Pass a single symbol to get a JSON object, or multiple comma-separated
    symbols to get a JSON array.
    Use `GET /market/commodities` to retrieve the list of valid commodity symbols.
    Cached for 30 seconds.

    - **symbols**: One or more commodity symbols (e.g. `GC` or `GC,SI,CL`)
    """
    syms = [s.strip().upper() for s in symbols.split(",")]
    cache_key = f"commodity_based_real_time_quotes:{','.join(sorted(syms))}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        commodity_based_real_time_quotes_data = await eodhd.get_commodity_based_real_time_quotes_data(symbols=syms)
        await cache.set_cache(cache_key, commodity_based_real_time_quotes_data, settings.COMMODITY_BASED_REAL_TIME_QUOTES_CACHE_TTL)
        return commodity_based_real_time_quotes_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/")
async def list_commodities():
    """
    List all supported commodities.

    Returns the full catalogue of commodities available in this API, covering
    metals, energy, and agricultural products. Use the `symbol` field from
    this response as the `commodity` path parameter in other commodity endpoints.
    """
    return [
        {"symbol": symbol, "name": name}
        for symbol, name in VALID_COMMODITIES.items()
    ]
        