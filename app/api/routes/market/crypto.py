from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings


router = APIRouter(
    prefix="/market/crypto",
    tags=["Crypto"],
)

eodhd = EodhdClient()

VALID_CRYPTO = {
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "SOL-USD": "Solana",
    "BNB-USD": "BNB",
    "XRP-USD": "XRP",
    "USDC-USD": "USD Coin",
    "ADA-USD": "Cardano",
    "AVAX-USD": "Avalanche",
    "DOGE-USD": "Dogecoin",
    "TRX-USD": "TRON",
}


@router.get("/real-time-quotes")
async def get_crypto_real_time_quotes_data(
    symbols: str = Query(..., description="Comma-separated crypto symbols (e.g. `BTC-USD` or `BTC-USD,ETH-USD,SOL-USD`)"),
):
    """
    Get real-time quotes for one or more cryptocurrencies.

    Pass a single symbol to get a JSON object, or multiple comma-separated
    symbols to get a JSON array.
    Use `GET /market/crypto` to retrieve the list of valid symbols.
    Cached for 15 seconds.

    - **symbols**: One or more crypto symbols (e.g. `BTC-USD` or `BTC-USD,ETH-USD,SOL-USD`)
    """
    syms = [s.strip().upper() for s in symbols.split(",")]
    cache_key = f"crypto_real_time_quotes:{','.join(sorted(syms))}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        crypto_data = await eodhd.get_crypto_real_time_quotes_data(symbols=syms)
        await cache.set_cache(cache_key, crypto_data, settings.CRYPTO_REAL_TIME_QUOTES_CACHE_TTL)
        return crypto_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/{symbol}/fundamentals")
async def get_crypto_fundamentals(symbol: str):
    """
    Get fundamental statistics for a cryptocurrency.

    Returns market cap, diluted market cap, circulating supply, max supply,
    market dominance, and all-time high/low from EODHD.
    Use `GET /market/crypto` to retrieve the list of valid symbols.
    Cached for 5 minutes.

    - **symbol**: Crypto symbol (e.g. `BTC-USD`)
    """
    sym = symbol.upper()
    if sym not in VALID_CRYPTO:
        raise HTTPException(status_code=400, detail=f"Unsupported symbol '{sym}'. Use GET /market/crypto for the full list.")

    cache_key = f"crypto_fundamentals:{sym}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data

    try:
        data = await eodhd.get_crypto_fundamentals_data(symbol=sym)
        result = data.get("Statistics", {})
        await cache.set_cache(cache_key, result, settings.CRYPTO_FUNDAMENTALS_CACHE_TTL)
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/")
async def list_crypto():
    """
    List all supported cryptocurrencies.

    Returns the full catalogue of crypto assets available in this API.
    Use the `symbol` field from this response as the `symbol` path parameter
    in other crypto endpoints.
    """
    return [
        {"symbol": symbol, "name": name}
        for symbol, name in VALID_CRYPTO.items()
    ]
