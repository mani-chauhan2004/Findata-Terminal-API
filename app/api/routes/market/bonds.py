import asyncio
from datetime import date, timedelta
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
    # US
    "US1Y":  "US 1-Year Treasury",
    "US2Y":  "US 2-Year Treasury",
    "US5Y":  "US 5-Year Treasury",
    "US10Y": "US 10-Year Treasury",
    "US30Y": "US 30-Year Treasury",
    # Germany
    "DE1Y":  "Germany 1-Year Bond",
    "DE2Y":  "Germany 2-Year Schatz",
    "DE5Y":  "Germany 5-Year Bond",
    "DE10Y": "Germany 10-Year Bund",
    "DE30Y": "Germany 30-Year Bond",
    # United Kingdom
    "UK1Y":  "UK 1-Year Gilt",
    "UK2Y":  "UK 2-Year Gilt",
    "UK5Y":  "UK 5-Year Gilt",
    "UK10Y": "UK 10-Year Gilt",
    "UK30Y": "UK 30-Year Gilt",
    # Spain
    "ES1Y":  "Spain 1-Year Bond",
    "ES5Y":  "Spain 5-Year Bond",
    "ES10Y": "Spain 10-Year Bond",
    # Italy
    "IT1Y":  "Italy 1-Year Bond",
    "IT2Y":  "Italy 2-Year CTZ",
    "IT5Y":  "Italy 5-Year Bond",
    "IT10Y": "Italy 10-Year BTP",
    "IT30Y": "Italy 30-Year Bond",
    # Japan
    "JP5Y":  "Japan 5-Year JGB",
    "JP10Y": "Japan 10-Year JGB",
    "JP30Y": "Japan 30-Year JGB",
    # China
    "CN1Y":  "China 1-Year Bond",
    "CN2Y":  "China 2-Year Bond",
    "CN5Y":  "China 5-Year Bond",
    "CN10Y": "China 10-Year Bond",
    "CN30Y": "China 30-Year Bond",
}

GLOBAL_YIELDS_COUNTRIES = [
    {"country": "United States", "code": "US",  "5Y": "US5Y",  "10Y": "US10Y"},
    {"country": "Germany",       "code": "DE",  "5Y": "DE5Y",  "10Y": "DE10Y"},
    {"country": "United Kingdom","code": "UK",  "5Y": "UK5Y",  "10Y": "UK10Y"},
    {"country": "Spain",         "code": "ES",  "5Y": "ES5Y",  "10Y": "ES10Y"},
    {"country": "Italy",         "code": "IT",  "5Y": "IT5Y",  "10Y": "IT10Y"},
    {"country": "Japan",         "code": "JP",  "5Y": "JP5Y",  "10Y": "JP10Y"},
    {"country": "China",         "code": "CN",  "5Y": "CN5Y",  "10Y": "CN10Y"},
]


@router.get("/global-yields")
async def get_global_yields():
    """
    Get the latest 5Y and 10Y government bond yields for major economies.

    Returns the most recent yield for United States, Germany, United Kingdom,
    Spain, Italy, Japan, and China. Cached for 1 hour.
    """
    cache_key = "bond_global_yields"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    from_date = (date.today() - timedelta(days=7)).isoformat()

    async def fetch_latest_yield(symbol: str) -> float | None:
        try:
            data = await eodhd.get_bond_historical_eod_data(bond=symbol, from_date=from_date)
            if data:
                return data[-1]["close"]
        except Exception:
            pass
        return None

    all_symbols = [c["5Y"] for c in GLOBAL_YIELDS_COUNTRIES] + [c["10Y"] for c in GLOBAL_YIELDS_COUNTRIES]
    results = await asyncio.gather(*[fetch_latest_yield(s) for s in all_symbols])
    yields_map = dict(zip(all_symbols, results))

    response = [
        {
            "country": c["country"],
            "code": c["code"],
            "5Y": yields_map.get(c["5Y"]),
            "10Y": yields_map.get(c["10Y"]),
        }
        for c in GLOBAL_YIELDS_COUNTRIES
    ]

    await cache.set_cache(cache_key, response, settings.BOND_HISTORICAL_EOD_CACHE_TTL)
    return response


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
