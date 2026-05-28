from fastapi import APIRouter, HTTPException
from app.services.sheets_client import sheets_client
from app.services.cache import cache

router = APIRouter(
    prefix="/market",
    tags=["Symbols"],
)

_STOCK_SYMBOLS_CACHE_KEY = "market:symbols"
_NEWS_SYMBOLS_CACHE_KEY = "market:news:symbols"
_COUNTRY_FLAGS_CACHE_KEY = "market:country:flags"
_ALL_SYMBOLS_CACHE_KEY = "market:all:symbols"
_TOKENS_CACHE_KEY = "market:tokens"
_CACHE_TTL = 86400  # 24h — sheet rarely changes


@router.get("/symbols")
async def get_symbols():
    """
    Returns the curated list of supported symbols with metadata
    (ticker, name, logo URL, Twitter, LinkedIn). Cached for 24 hours.
    """
    cached = await cache.get_cache(_STOCK_SYMBOLS_CACHE_KEY)
    if cached is not None:
        return cached

    try:
        data = sheets_client.get_symbols()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(_STOCK_SYMBOLS_CACHE_KEY, data, _CACHE_TTL)
    return data

@router.get("/all-symbols")
async def get_all_symbols():
    """
    Returns all symbols with ticker, logo URL, and company name
    sourced from the symbols spreadsheet (sheet index 3).
    Cached for 24 hours.
    """
    cached = await cache.get_cache(_ALL_SYMBOLS_CACHE_KEY)
    if cached is not None:
        return cached

    try:
        data = sheets_client.get_all_symbols()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(_ALL_SYMBOLS_CACHE_KEY, data, _CACHE_TTL)
    return data


@router.get("/country-flags")
async def get_country_flags():
    """
    Returns country flag URLs sourced from the symbols spreadsheet (sheet index 2).
    Cached for 24 hours.
    """
    cached = await cache.get_cache(_COUNTRY_FLAGS_CACHE_KEY)
    if cached is not None:
        return cached

    try:
        data = sheets_client.get_country_flags()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(_COUNTRY_FLAGS_CACHE_KEY, data, _CACHE_TTL)
    return data


@router.get("/news/symbols")
async def get_news_portal_symbols():
    """
    Returns news portal symbols with logo URLs. Cached for 24 hours.
    """
    cached = await cache.get_cache(_NEWS_SYMBOLS_CACHE_KEY)
    if cached is not None:
        return cached

    try:
        data = sheets_client.get_news_portal_symbols()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(_NEWS_SYMBOLS_CACHE_KEY, data, _CACHE_TTL)
    return data


@router.get("/tokens")
async def get_tokens():
    """
    Returns on-chain tokens with name, symbol, contract address, and logo URL.
    Cached for 24 hours.
    """
    cached = await cache.get_cache(_TOKENS_CACHE_KEY)
    if cached is not None:
        return cached

    try:
        data = sheets_client.get_tokens()
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    await cache.set_cache(_TOKENS_CACHE_KEY, data, _CACHE_TTL)
    return data
