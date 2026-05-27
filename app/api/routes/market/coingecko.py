from typing import Literal
from fastapi import APIRouter, Query
from app.services.coingecko_client import CoinGeckoClient
from app.services.cache import cache
from app.core.config import settings

router = APIRouter(
    prefix="/market/crypto",
    tags=["Crypto"],
)

coingecko = CoinGeckoClient()

CoinOrder = Literal[
    "market_cap_desc",
    "market_cap_asc",
    "volume_asc",
    "volume_desc",
    "id_asc",
    "id_desc",
]


@router.get("/market-cap")
async def get_crypto_market_cap(
    ids: str = Query(..., description="Comma-separated CoinGecko coin IDs (e.g. `bitcoin,ethereum,arbitrum`)"),
    order: CoinOrder = Query("market_cap_desc", description="Sort order for results"),
):
    """
    Get market cap data for one or more cryptocurrencies via CoinGecko.

    Returns price, market cap, 24h volume, and 24h change for each coin.
    Cached for 60 seconds.

    - **ids**: Comma-separated CoinGecko coin IDs (e.g. `bitcoin,ethereum,arbitrum`)
    - **order**: Sort order — one of `market_cap_desc`, `market_cap_asc`, `volume_asc`, `volume_desc`, `id_asc`, `id_desc`
    """
    normalized_ids = ",".join(i.strip().lower() for i in ids.split(","))
    cache_key = f"coingecko_market_cap:{normalized_ids}:{order}"
    cached = await cache.get_cache(cache_key)
    if cached is not None:
        return cached

    data = await coingecko.get_market_cap_data(ids=normalized_ids, order=order)
    await cache.set_cache(cache_key, data, settings.COINGECKO_MARKET_CAP_CACHE_TTL)
    return data
