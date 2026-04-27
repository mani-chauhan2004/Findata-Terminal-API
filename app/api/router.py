from app.api.routes.stock import quote
from app.api.routes.stock import historical
from app.api.routes.stock import fundamental
from app.api.routes.stock import dividends
from app.api.routes.stock import insider_trades
from app.api.routes.stock import news
from app.api.routes.market import indices
from app.api.routes.market import bonds
from app.api.routes.market import quotes
from app.api.routes.market import historical
from app.api.routes.market import commodities
from app.api.routes.market import crypto
from app.api.routes.market import screener
from app.api.routes.market import news as market_news
from app.api.routes.calendar import earnings
from app.api.routes.calendar import ipo
from app.api.routes.calendar import splits as split
from app.api.routes.calendar import dividends as dividend
from app.api.routes.calendar import economic
from fastapi import APIRouter

router = APIRouter()

router.include_router(quote.router)
router.include_router(historical.router)
router.include_router(fundamental.router)
router.include_router(dividends.router)
router.include_router(insider_trades.router)
router.include_router(news.router)
router.include_router(quotes.router)
router.include_router(historical.router)
router.include_router(indices.router)
router.include_router(bonds.router)
router.include_router(commodities.router)
router.include_router(crypto.router)
router.include_router(market_news.router)
router.include_router(screener.router)
router.include_router(earnings.router)
router.include_router(ipo.router)
router.include_router(split.router)
router.include_router(dividend.router)
router.include_router(economic.router)