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
