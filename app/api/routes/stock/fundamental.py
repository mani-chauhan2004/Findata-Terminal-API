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
    filter: str | None = Query(None, description="The filter to apply to the fundamental data")
):
    """
    Get fundamental company data for a stock.

    Returns detailed financial and company data sourced from EODHD. Use the
    optional `filter` parameter to request a specific section of the data.
    Omitting `filter` returns the full fundamental payload. Cache TTL varies
    by filter (1 hour for fast-changing data, 24 hours for slow-changing data).

    **Valid `filter` values:**

    | Filter | Description |
    |---|---|
    | `General` | Company profile, sector, industry, description |
    | `Highlights` | Key metrics: EPS, P/E, market cap |
    | `SharesStats` | Share structure, float, short interest |
    | `Valuation` | Enterprise value, EV/EBITDA, P/S ratios |
    | `Technicals` | 52-week range, moving averages, beta |
    | `AnalystRatings` | Consensus ratings and price targets |
    | `Earnings::History` | Historical EPS actuals vs. estimates |
    | `Earnings::Trend` | Forward EPS and revenue estimates |
    | `Financials::Income_Statement::yearly` | Annual income statement |
    | `Financials::Income_Statement::quarterly` | Quarterly income statement |
    | `Financials::Balance_Sheet::yearly` | Annual balance sheet |
    | `Financials::Balance_Sheet::quarterly` | Quarterly balance sheet |
    | `Financials::Cash_Flow::yearly` | Annual cash flow statement |
    | `Financials::Cash_Flow::quarterly` | Quarterly cash flow statement |

    - **symbol**: Stock ticker (e.g. `AAPL`)
    - **filter**: Data section to return (optional — returns full payload if omitted)
    """
    if filter is not None and filter not in VALID_FILTERS:
        raise HTTPException(status_code=400, detail="Invalid filter, available filters are: " + ", ".join(VALID_FILTERS))
    
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
