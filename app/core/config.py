from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Annotated, Literal
from pydantic import AnyUrl, BeforeValidator, computed_field

from app.core.paths import PROJECT_ROOT

_env_file = PROJECT_ROOT / ".env"

def parse_cors(v: any) -> list[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.split for i in v.split(",") if i.split()]
    elif isinstance(v, str | list):
        return v
    else: 
        raise ValueError("[CORS] Invalid CORS configuration, accepts only list of urls or string")

class settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file = str(_env_file),
        env_file_encoding = "utf-8",
        case_sensitive = True,
        env_prefix = "TERMINAL_",
        env_prefix_target = "variable",
        nested_model_default_partial_update = False,
    )

    API_V1_STR: str = "api/v1"
    FRONTEND_HOSTS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = []
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    @computed_field
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip('/') for origin in self.BACKEND_CORS_ORIGINS] + self.FRONTEND_HOSTS


    PROJECT_NAME: str

    ADMIN_KEY: str

    COINGECKO_API_KEY: str
    COINGECKO_API_BASE_URL: str

    EODHD_API_KEY: str
    EODHD_API_BASE_URL: str

    REDIS_URL: str

    # CoinGecko TTLs
    COINGECKO_MARKET_CAP_CACHE_TTL: int = 3600

    # Quote TTLs
    MIXED_REAL_TIME_QUOTES_CACHE_TTL: int = 15
    REALTIME_QUOTE_CACHE_TTL: int = 15
    US_QUOTE_DELAYED_CACHE_TTL: int = 60

    # Historical / EOD TTLs
    INTRADAY_CACHE_TTL: int = 60
    GENERIC_EOD_CACHE_TTL: int = 3600
    HISTORICAL_EOD_CACHE_TTL: int = 3600
    INDEX_BASED_REAL_TIME_QUOTES_CACHE_TTL: int = 30
    INDEX_BASED_HISTORICAL_EOD_CACHE_TTL: int = 3600
    BOND_HISTORICAL_EOD_CACHE_TTL: int = 3600
    COMMODITY_BASED_REAL_TIME_QUOTES_CACHE_TTL: int = 30
    FOREX_REAL_TIME_QUOTES_CACHE_TTL: int = 15
    CRYPTO_REAL_TIME_QUOTES_CACHE_TTL: int = 15
    CRYPTO_FUNDAMENTALS_CACHE_TTL: int = 300

    # News TTL
    NEWS_CACHE_TTL: int = 300

    # Screener TTL
    SCREENER_CACHE_TTL: int = 300

    # Insider transactions TTL
    INSIDER_TRANSACTIONS_CACHE_TTL: int = 3600

    # Calendar TTLs
    DIVIDEND_CALENDAR_CACHE_TTL: int = 3600
    EARNINGS_CALENDAR_CACHE_TTL: int = 3600
    IPO_CALENDAR_CACHE_TTL: int = 3600
    SPLIT_CALENDAR_CACHE_TTL: int = 3600
    ECONOMIC_CALENDAR_CACHE_TTL: int = 1800

    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_JSON: str
    SYMBOLS_SPREADSHEET_ID: str

    # Fundamentals TTLs
    FUNDAMENTAL_DEFAULT_CACHE_TTL: int = 3600
    FUNDAMENTAL_GENERAL_CACHE_TTL: int = 86400
    FUNDAMENTAL_HIGHLIGHTS_CACHE_TTL: int = 3600
    FUNDAMENTAL_SHARES_STATS_CACHE_TTL: int = 86400
    FUNDAMENTAL_VALUATION_CACHE_TTL: int = 3600
    FUNDAMENTAL_TECHNICALS_CACHE_TTL: int = 3600
    FUNDAMENTAL_ANALYST_RATINGS_CACHE_TTL: int = 86400
    FUNDAMENTAL_EARNINGS_HISTORY_CACHE_TTL: int = 86400
    FUNDAMENTAL_EARNINGS_TREND_CACHE_TTL: int = 86400
    FUNDAMENTAL_INCOME_STATEMENT_YEARLY_CACHE_TTL: int = 86400
    FUNDAMENTAL_INCOME_STATEMENT_QUARTERLY_CACHE_TTL: int = 86400
    FUNDAMENTAL_BALANCE_SHEET_YEARLY_CACHE_TTL: int = 86400
    FUNDAMENTAL_BALANCE_SHEET_QUARTERLY_CACHE_TTL: int = 86400
    FUNDAMENTAL_CASH_FLOW_YEARLY_CACHE_TTL: int = 86400
    FUNDAMENTAL_CASH_FLOW_QUARTERLY_CACHE_TTL: int = 86400


settings = settings()
    


