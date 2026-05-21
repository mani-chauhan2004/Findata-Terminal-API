from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings
from app.core.market_classification import MSCI_CLASSIFICATION

router = APIRouter(prefix="/market/indices", tags=["Indices"])
eodhd = EodhdClient()

VALID_INDICES: dict[str, dict] = {
    # US
    "GSPC":     {"name": "S&P 500",              "country_iso2": "US"},
    "DJI":      {"name": "Dow Jones",             "country_iso2": "US"},
    "IXIC":     {"name": "Nasdaq Composite",      "country_iso2": "US"},
    "RUT":      {"name": "Russell 2000",          "country_iso2": "US"},
    # Europe
    "FTSE":     {"name": "FTSE 100",              "country_iso2": "GB"},
    "GDAXI":    {"name": "DAX",                   "country_iso2": "DE"},
    "FCHI":     {"name": "CAC 40",                "country_iso2": "FR"},
    "STOXX50E": {"name": "Euro Stoxx 50",         "country_iso2": "EU"},
    # Asia - Developed
    "N225":     {"name": "Nikkei 225",            "country_iso2": "JP"},
    "HSI":      {"name": "Hang Seng",             "country_iso2": "HK"},
    "AXJO":     {"name": "ASX 200",               "country_iso2": "AU"},
    # Asia - Emerging
    "000001":   {"name": "Shanghai Composite",    "country_iso2": "CN"},
    "KS11":     {"name": "KOSPI",                 "country_iso2": "KR"},
    "NSEI":     {"name": "Nifty 50",              "country_iso2": "IN"},
    # Americas - Emerging
    "BVSP":     {"name": "Bovespa",               "country_iso2": "BR"},
    "MXX":      {"name": "IPC Mexico",            "country_iso2": "MX"},
    # Africa - Emerging
    "J203":     {"name": "JSE All Share",         "country_iso2": "ZA"},
}


def _attach_classification(sym: str) -> dict:
    meta = VALID_INDICES[sym]
    return {
        "market_type": MSCI_CLASSIFICATION.get(meta["country_iso2"], "Unknown"),
        "country_iso2": meta["country_iso2"],
    }


@router.get("/real-time-quotes")
async def get_index_based_real_time_quotes_data(
    symbols: str = Query(..., description="Comma-separated index symbols (e.g. `GSPC` or `GSPC,DJI,IXIC`)"),
):
    """
    Get real-time quotes for one or more market indices.

    Pass a single symbol to get a JSON object, or multiple comma-separated
    symbols to get a JSON array. Each result is enriched with `market_type`
    and `country_iso2` derived from the MSCI classification.
    Use `GET /market/indices` to retrieve the list of valid index symbols.
    Cached for 30 seconds.

    - **symbols**: One or more index symbols (e.g. `GSPC` or `GSPC,DJI,IXIC`)
    """
    syms = [s.strip().upper() for s in symbols.split(",")]
    invalid = [s for s in syms if s not in VALID_INDICES]
    if invalid:
        raise HTTPException(status_code=400, detail=f"Unsupported index symbols: {', '.join(invalid)}")

    cache_key = f"index_based_real_time_quotes:{','.join(sorted(syms))}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        data = await eodhd.get_index_based_real_time_quotes_data(symbols=syms)

        if isinstance(data, list):
            filtered = []
            for item in data:
                if item.get("close") == "NA":
                    continue
                sym = item.get("code", "").upper()
                if sym in VALID_INDICES:
                    item.update(_attach_classification(sym))
                filtered.append(item)
            data = filtered
        elif isinstance(data, dict):
            if data.get("close") == "NA":
                return []
            sym = data.get("code", "").upper()
            if sym in VALID_INDICES:
                data.update(_attach_classification(sym))

        await cache.set_cache(cache_key, data, settings.INDEX_BASED_REAL_TIME_QUOTES_CACHE_TTL)
        return data
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
        data = await eodhd.get_index_based_historical_eod_data(index=index, from_date=from_date, to_date=to_date)
        await cache.set_cache(cache_key, data, settings.INDEX_BASED_HISTORICAL_EOD_CACHE_TTL)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/")
async def list_indices(
    market_type: str | None = Query(None, description="Filter by market type: `Developed`, `Emerging`, or `Frontier`"),
):
    """
    List all supported market indices.

    Returns the full catalogue of indices available in this API, each enriched
    with its MSCI `market_type` (Developed, Emerging, Frontier) and `country_iso2`.
    Use the optional `market_type` query param to filter by classification.
    Use the `symbol` field from this response as the `symbols` query parameter
    in the real-time-quotes endpoint.

    - **market_type**: Optional filter (`Developed`, `Emerging`, `Frontier`)
    """
    result = [
        {
            "symbol": sym,
            "name": meta["name"],
            "country_iso2": meta["country_iso2"],
            "market_type": MSCI_CLASSIFICATION.get(meta["country_iso2"], "Unknown"),
        }
        for sym, meta in VALID_INDICES.items()
    ]

    if market_type:
        result = [r for r in result if r["market_type"].lower() == market_type.lower()]

    return result
