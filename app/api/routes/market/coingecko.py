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


@router.get("/token-overview")
async def get_token_overview(
    contract_address: str = Query(..., description="Token contract address (e.g. `0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9`)"),
    platform: str = Query("arbitrum-one", description="CoinGecko asset platform ID (e.g. `arbitrum-one`, `ethereum`)"),
):
    """
    Get full token overview by contract address via CoinGecko.

    Returns name, symbol, description, chain, categories, price, market cap,
    24h volume, circulating supply, all-time high, and explorer links.
    Cached for 1 hour.
    """
    normalized_address = contract_address.strip().lower()
    cache_key = f"coingecko_token_overview:{platform}:{normalized_address}"
    cached = await cache.get_cache(cache_key)
    if cached is not None:
        return cached

    raw = await coingecko.get_token_info(platform=platform, contract_address=normalized_address)

    market = raw.get("market_data", {})
    detail_platforms = raw.get("detail_platforms", {})
    platform_detail = detail_platforms.get(platform, {})

    explorer_links = [
        link for link in raw.get("links", {}).get("blockchain_site", []) if link
    ]

    data = {
        "id": raw.get("id"),
        "name": raw.get("name"),
        "symbol": raw.get("symbol", "").upper(),
        "contract_address": platform_detail.get("contract_address") or normalized_address,
        "platform": platform,
        "description": raw.get("description", {}).get("en", ""),
        "categories": raw.get("categories", []),
        "image": raw.get("image", {}).get("large"),
        "price_usd": market.get("current_price", {}).get("usd"),
        "market_cap_usd": market.get("market_cap", {}).get("usd"),
        "volume_24h_usd": market.get("total_volume", {}).get("usd"),
        "circulating_supply": market.get("circulating_supply"),
        "ath_usd": market.get("ath", {}).get("usd"),
        "ath_date": market.get("ath_date", {}).get("usd"),
        "explorer_links": explorer_links,
        "coingecko_url": f"https://www.coingecko.com/en/coins/{raw.get('id', '')}",
    }

    await cache.set_cache(cache_key, data, settings.COINGECKO_TOKEN_INFO_CACHE_TTL)
    return data


@router.get("/token-price")
async def get_token_price(
    contract_addresses: str = Query(..., description="Comma-separated contract addresses (e.g. `0xaf88d065e77c8cC2239327C5EDb3A432268e5831`)"),
    platform: str = "arbitrum-one",
    vs_currencies: str = Query("usd", description="Comma-separated target currencies (e.g. `usd,eth`)"),
    include_24hr_vol: bool = Query(False, description="Include 24h trading volume"),
    include_24hr_change: bool = Query(False, description="Include 24h price change percentage"),
):
    """
    Get price and market cap for on-chain tokens by contract address via CoinGecko.

    Market cap is always included. Platform defaults to `arbitrum-one`.
    Cached for 60 seconds.

    - **contract_addresses**: One or more contract addresses (comma-separated)
    - **platform**: CoinGecko asset platform ID (default: `arbitrum-one`)
    - **vs_currencies**: Target currencies (default: `usd`)
    - **include_24hr_vol**: Include 24h volume in response
    - **include_24hr_change**: Include 24h change % in response
    """
    normalized_addresses = ",".join(a.strip().lower() for a in contract_addresses.split(","))
    cache_key = f"coingecko_token_price:{platform}:{normalized_addresses}:{vs_currencies}:{include_24hr_vol}:{include_24hr_change}"
    cached = await cache.get_cache(cache_key)
    if cached is not None:
        return cached

    data = await coingecko.get_token_price_data(
        platform=platform,
        contract_addresses=normalized_addresses,
        vs_currencies=vs_currencies,
        include_24hr_vol=include_24hr_vol,
        include_24hr_change=include_24hr_change,
    )
    await cache.set_cache(cache_key, data, settings.COINGECKO_TOKEN_PRICE_CACHE_TTL)
    return data
