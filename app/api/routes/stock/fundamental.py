from fastapi import APIRouter, HTTPException, Query
from app.services.eodhd_client import EodhdClient
from app.services.cache import cache
from app.core.config import settings


router = APIRouter(
    prefix="/stock",
    tags=["fundamental"],
)

eodhd = EodhdClient()

VALID_FILTERS = {
    "General",
    "Highlights",
    "SharesStats",
    "Valuation",
    "Technicals",
    "AnalystRatings",
    "Earnings::History",
    "Earnings::Trend",
    "Financials::Income_Statement::yearly",
    "Financials::Income_Statement::quarterly",
    "Financials::Balance_Sheet::yearly",
    "Financials::Balance_Sheet::quarterly",
    "Financials::Cash_Flow::yearly",
    "Financials::Cash_Flow::quarterly",
}

FILTER_TTL_MAP = {
    "General": settings.FUNDAMENTAL_GENERAL_CACHE_TTL,
    "Highlights": settings.FUNDAMENTAL_HIGHLIGHTS_CACHE_TTL,
    "SharesStats": settings.FUNDAMENTAL_SHARES_STATS_CACHE_TTL,
    "Valuation": settings.FUNDAMENTAL_VALUATION_CACHE_TTL,
    "Technicals": settings.FUNDAMENTAL_TECHNICALS_CACHE_TTL,
    "AnalystRatings": settings.FUNDAMENTAL_ANALYST_RATINGS_CACHE_TTL,
    "Earnings::History": settings.FUNDAMENTAL_EARNINGS_HISTORY_CACHE_TTL,
    "Earnings::Trend": settings.FUNDAMENTAL_EARNINGS_TREND_CACHE_TTL,
    "Financials::Income_Statement::yearly": settings.FUNDAMENTAL_INCOME_STATEMENT_YEARLY_CACHE_TTL,
    "Financials::Income_Statement::quarterly": settings.FUNDAMENTAL_INCOME_STATEMENT_QUARTERLY_CACHE_TTL,
    "Financials::Balance_Sheet::yearly": settings.FUNDAMENTAL_BALANCE_SHEET_YEARLY_CACHE_TTL,
    "Financials::Balance_Sheet::quarterly": settings.FUNDAMENTAL_BALANCE_SHEET_QUARTERLY_CACHE_TTL,
    "Financials::Cash_Flow::yearly": settings.FUNDAMENTAL_CASH_FLOW_YEARLY_CACHE_TTL,
    "Financials::Cash_Flow::quarterly": settings.FUNDAMENTAL_CASH_FLOW_QUARTERLY_CACHE_TTL,
}

@router.get("/{symbol}/fundamental")
async def get_fundamental_data(
    symbol: str, 
    filter: str = Query(..., description="The filter to apply to the fundamental data")
):
    if filter not in VALID_FILTERS:
        raise HTTPException(status_code=400, detail="Invalid filter, available filters are: " + ", ".join(VALID_FILTERS.keys()))
    
    sym = symbol.upper()
    cache_key = f"fundamental:{sym}:{filter}"
    cached_data = await cache.get_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    try:
        fundamental_data = await eodhd.get_fundamentals_data(symbol=sym, filter=filter)
        ttl = FILTER_TTL_MAP.get(filter, settings.FUNDAMENTAL_DEFAULT_CACHE_TTL)
        await cache.set_cache(cache_key, fundamental_data, ttl)
        return fundamental_data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
