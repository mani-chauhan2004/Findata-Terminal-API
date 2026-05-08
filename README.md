# ASXN Terminal API Documentation

> **Version**: v1
> **Base URL**: `http://localhost:8000/api/v1`
> **Last Updated**: 2026-05-08

---

## Table of Contents

1. [Overview](#overview)
2. [Setup Guide](#setup-guide)
3. [Getting Started](#getting-started)
4. [Authentication](#authentication)
5. [Versioning](#versioning)
6. [Request & Response Format](#request--response-format)
7. [Error Handling](#error-handling)
8. [Caching](#caching)
9. [Stock Endpoints](#stock-endpoints)
10. [Calendar Endpoints](#calendar-endpoints)
11. [Market Endpoints](#market-endpoints)
12. [Health](#health)
13. [Workflows & Common Use Cases](#workflows--common-use-cases)
14. [Reference: Parameters & Types](#reference-parameters--types)

---

## Overview

The ASXN Terminal API is a financial data proxy service that provides real-time and historical market data for stocks, indices, commodities, crypto, and financial calendars. It is built on top of the [EODHD](https://eodhd.com) data provider and adds Redis-backed caching to reduce latency and upstream load.

**Who is this for?**
- **Developers** integrating financial data into front-end dashboards or trading tools
- **Data engineers** fetching bulk historical or fundamental data
- **Product teams** building screens, alerts, or portfolio analytics

**Key capabilities:**
- Real-time and delayed stock quotes (single or batch)
- End-of-day (EOD) historical price data
- Intraday OHLCV bars (1m, 5m, 1h)
- Generic EOD data across any exchange type (stocks, crypto, indices, commodities)
- Mixed real-time quotes across multiple asset classes in a single call
- Fundamental company data (income statements, balance sheets, cash flows, valuations)
- Insider transaction data
- Stock, market, and financial news
- Economic, earnings, dividend, split, and IPO calendars
- Market screener with gainers, losers, and most-active filters
- Global index and commodity quotes
- Cryptocurrency quotes
- Government bond historical data

---

## Setup Guide

### Prerequisites

| Requirement | Minimum Version | Notes |
|---|---|---|
| Python | 3.11+ | 3.14 used in development |
| Redis | 7.x | Must be running before starting the server |
| EODHD API key | — | Sign up at [eodhd.com](https://eodhd.com) — use `demo` for limited testing |

### 1. Clone the repository

```bash
git clone <repository-url>
cd asxn_terminal
```

### 2. Create and activate a virtual environment

```bash
python -m venv terminal_venv
source terminal_venv/bin/activate   # macOS / Linux
terminal_venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

**Installed packages:**

| Package | Purpose |
|---|---|
| `fastapi` | Web framework and OpenAPI generation |
| `uvicorn` | ASGI server |
| `gunicorn` | Production process manager |
| `pydantic` / `pydantic-settings` | Data validation and `.env` config loading |
| `aiohttp` | Async HTTP client (upstream requests) |
| `httpx` | HTTP client for service calls |
| `redis` | Redis client for caching |
| `python-dotenv` | `.env` file loading |

### 4. Configure environment variables

The app loads configuration exclusively from `.env` (hardcoded in `app/core/config.py`).
Edit it directly and replace the placeholder values:

**Required variables:**

```dotenv
TERMINAL_PROJECT_NAME=Terminal
TERMINAL_EODHD_API_KEY=your_eodhd_api_key_here
TERMINAL_EODHD_API_BASE_URL=https://eodhd.com
TERMINAL_REDIS_URL=redis://localhost:6379
```

**Optional overrides** (defaults shown):

```dotenv
TERMINAL_HOST=0.0.0.0
TERMINAL_PORT=8000
TERMINAL_ENVIRONMENT=local          # local | staging | production
TERMINAL_API_V1_STR=api/v1
TERMINAL_BACKEND_CORS_ORIGINS=[http://localhost:3000,http://localhost:8000]
```

> **Note:** All environment variables must be prefixed with `TERMINAL_`. The application will fail to start if `TERMINAL_PROJECT_NAME`, `TERMINAL_EODHD_API_KEY`, `TERMINAL_EODHD_API_BASE_URL`, or `TERMINAL_REDIS_URL` are missing.

> **EODHD demo key:** The `demo` API key is accepted by EODHD for a small subset of endpoints and symbols (e.g. `AAPL.US`). Use a paid key for full access.

### 5. Start Redis

**macOS (Homebrew):**
```bash
brew services start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:7
```

**Verify Redis is running:**
```bash
redis-cli ping   # should return PONG
```

### 6. Start the server

**Development (with auto-reload):**
```bash
python -m app.main
```

**Alternative — uvicorn directly:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Production (gunicorn + uvicorn workers):**
```bash
gunicorn app.main:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:8000
```

### 7. Verify the server is running

```bash
curl http://localhost:8000/api/v1/stock/quote?symbols=AAPL
```

You should receive a JSON quote response. The interactive Swagger UI is available at `http://localhost:8000/docs` when `TERMINAL_ENVIRONMENT=local`.

### Environment Summary

| Variable | Required | Default | Description |
|---|---|---|---|
| `TERMINAL_PROJECT_NAME` | Yes | — | Application name shown in Swagger UI |
| `TERMINAL_EODHD_API_KEY` | Yes | — | EODHD API key |
| `TERMINAL_EODHD_API_BASE_URL` | Yes | — | EODHD base URL |
| `TERMINAL_REDIS_URL` | Yes | — | Redis connection string |
| `TERMINAL_HOST` | No | `0.0.0.0` | Server bind host |
| `TERMINAL_PORT` | No | `8000` | Server bind port |
| `TERMINAL_ENVIRONMENT` | No | `local` | Controls Swagger UI visibility |
| `TERMINAL_API_V1_STR` | No | `api/v1` | API version prefix |
| `TERMINAL_BACKEND_CORS_ORIGINS` | No | `[]` | Allowed CORS origins |

---

## Getting Started

Your first call should return a real-time quote in under 5 minutes.

### Step 1 — Verify the API is running

```bash
curl http://localhost:8000/api/v1/stock/quote?symbols=AAPL
```

### Step 2 — Explore the auto-generated docs

| Environment | URL |
|---|---|
| Local | `http://localhost:8000/docs` (Swagger UI) |
| Local | `http://localhost:8000/redoc` (ReDoc) |
| Staging / Production | Not exposed |

### Step 3 — Make your first meaningful call

Fetch the last 30 days of historical prices for Apple:

```bash
curl "http://localhost:8000/api/v1/stock/AAPL/historical?from=2025-02-01&to=2025-03-01"
```

---

## Authentication

The ASXN Terminal API does **not** require client-side authentication tokens on its own endpoints.

Authentication with the upstream EODHD data provider is handled server-side using the `EODHD_API_KEY` environment variable configured at deployment time. Clients consume the proxy directly without needing an EODHD key.

> **Security note**: All EODHD credentials are stored as server-side environment variables and are never exposed in API responses or logs.

---

## Versioning

All endpoints are prefixed with `/api/v1`. Breaking changes will be introduced under a new version prefix (e.g., `/api/v2`). The current version (`v1`) will remain available during any migration window.

---

## Request & Response Format

### Request

- All requests use **HTTP GET**
- Parameters are passed as **path parameters** (`/stock/{symbol}/historical`) or **query parameters** (`?symbols=AAPL,TSLA`)
- Date values must follow **ISO 8601 format**: `YYYY-MM-DD`
- Unix timestamps (used in intraday) must be in **UTC**
- The `filters` parameter on the screener endpoint accepts a **JSON-encoded array** (URL-encoded when sent via query string)
- Multiple symbols are passed as a **comma-separated string** in a single `symbols` query parameter

### Response

- All responses return **JSON**
- Endpoints that accept multiple symbols return a **JSON array**; single-symbol calls return a **JSON object**
- Successful responses use HTTP `200`

---

## Error Handling

All endpoints return a consistent error structure:

```json
{
  "detail": "Human-readable error message"
}
```

### HTTP Status Codes

| Code | Meaning | Common Cause |
|---|---|---|
| `200` | OK | Request succeeded |
| `400` | Bad Request | Invalid or missing parameters (e.g., missing required `from`/`to`, invalid filter JSON) |
| `502` | Bad Gateway | Upstream EODHD API returned an error or is unreachable |
| `403` | Forbidden | Upstream EODHD API denied access to the endpoint |


### Error Examples

**Missing required date parameter:**
```json
{
  "detail": "Both 'from' and 'to' query parameters are required."
}
```

**Invalid screener filter JSON:**
```json
{
  "detail": "Invalid filters format. Expected a JSON array."
}
```

**Upstream service failure:**
```json
{
  "detail": "Service error: <upstream message>"
}
```

**Upstream service access denied:**
```json
{
  "detail": "Client error '403 Forbidden' for url {url}\nFor more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403"
}
```

---

## Caching

All endpoints use **Redis** for response caching. Cached responses are served instantly without hitting the upstream API.

| Endpoint Category | Cache TTL |
|---|---|
| Real-time stock quote | 15 seconds |
| Delayed US stock quote | 60 seconds |
| Mixed real-time quotes (multi-asset) | 15 seconds |
| Crypto real-time quotes | 15 seconds |
| Index real-time quotes | 30 seconds |
| Commodity real-time quotes | 30 seconds |
| Intraday OHLCV | 60 seconds |
| Historical EOD (stock) | 1 hour |
| Generic EOD (any exchange) | 1 hour |
| Bond historical EOD | 1 hour |
| Index historical EOD | 1 hour |
| Dividend (stock) | 1 hour |
| Insider transactions | 1 hour |
| Earnings calendar | 1 hour |
| Dividend calendar | 1 hour |
| Split calendar | 1 hour |
| IPO calendar | 1 hour |
| Fundamental data (fast-changing filters) | 1 hour |
| Stock news | 5 minutes |
| Market news | 5 minutes |
| Market screener | 5 minutes |
| Economic calendar | 30 minutes |
| Fundamental data (slow-changing filters) | 24 hours |

> Cache TTLs are configurable via environment variables. Stale data is never returned on cache miss — a fresh upstream request is always made.

---

## Stock Endpoints

### GET `/stock/quote`

Returns real-time quotes for one or more US stocks. Pass a single ticker to get a JSON object, or multiple comma-separated tickers to get a JSON array.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbols` | string | Yes | Comma-separated US ticker symbols (e.g. `AAPL` or `AAPL,TSLA,MSFT`) |

**Example Request — single symbol**

```bash
curl "http://localhost:8000/api/v1/stock/quote?symbols=AAPL"
```

**Example Request — multiple symbols**

```bash
curl "http://localhost:8000/api/v1/stock/quote?symbols=AAPL,TSLA,MSFT"
```

**Example Response**

```json
{
  "code": "AAPL.US",
  "timestamp": 1741200000,
  "gmtoffset": 0,
  "open": 227.20,
  "high": 229.85,
  "low": 226.50,
  "close": 228.87,
  "volume": 52134200,
  "previousClose": 226.51,
  "change": 2.36,
  "change_p": 1.042
}
```

**Cache TTL**: 15 seconds

---

### GET `/stock/{symbol}/quote/delayed`

Returns a delayed (15-min) US market quote. Available for US-listed securities only.

**Path Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | Yes | US stock ticker symbol |

**Example Request**

```bash
curl http://localhost:8000/api/v1/stock/AAPL/quote/delayed
```

**Cache TTL**: 60 seconds

---

### GET `/stock/{symbol}/historical`

Returns end-of-day (EOD) historical price data for a stock. Omit `from` and `to` to retrieve the full available history.

**Path Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | Yes | Stock ticker symbol |

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `from` | string | No | Start date in `YYYY-MM-DD` format |
| `to` | string | No | End date in `YYYY-MM-DD` format |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/stock/AAPL/historical?from=2025-01-01&to=2025-03-01"
```

**Example Response**

```json
[
  {
    "date": "2025-03-01",
    "open": 227.20,
    "high": 229.85,
    "low": 226.50,
    "close": 228.87,
    "adjusted_close": 228.87,
    "volume": 52134200
  }
]
```

**Cache TTL**: 1 hour

---

### GET `/stock/dividends`

Returns dividend data. Requires either a `symbol` or a `date_eq` parameter.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | Conditional | Stock ticker symbol |
| `date_eq` | string | Conditional | Exact ex-dividend date in `YYYY-MM-DD` format |
| `from` | string | No | Start date in `YYYY-MM-DD` format |
| `to` | string | No | End date in `YYYY-MM-DD` format |

> **Validation**: At least one of `symbol` or `date_eq` must be provided.

**Example Request — by symbol**

```bash
curl "http://localhost:8000/api/v1/stock/dividends?symbol=AAPL&from=2024-01-01&to=2025-01-01"
```

**Example Request — by date**

```bash
curl "http://localhost:8000/api/v1/stock/dividends?date_eq=2025-02-07"
```

**Cache TTL**: 1 hour

---

### GET `/stock/insider_transactions`

Returns insider trading transactions. Optionally filtered by symbol.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | No | Stock ticker symbol. If omitted, returns recent transactions across all securities |
| `limit` | integer | No | Number of transactions to return |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/stock/insider_transactions?symbol=TSLA&limit=20"
```

**Example Response**

```json
[
  {
    "date": "2025-02-15",
    "owner_name": "Elon Musk",
    "transaction_type": "Buy",
    "value": 15000000,
    "shares": 65000
  }
]
```

**Cache TTL**: 1 hour

---

### GET `/stock/{symbol}/fundamental`

Returns fundamental company data. Use the `filter` parameter to narrow the response to a specific data section.

**Path Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | Yes | Stock ticker symbol |

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `filter` | string | No | Fundamental data section to return (see valid values below) |

**Valid `filter` Values**

| Filter | Description | Cache TTL |
|---|---|---|
| `General` | Company profile, sector, industry, description | 24 hours |
| `Highlights` | Key financial highlights (EPS, P/E, market cap) | 1 hour |
| `SharesStats` | Share structure, float, short interest | 24 hours |
| `Valuation` | Enterprise value, EV/EBITDA, P/S ratios | 1 hour |
| `Technicals` | 52-week range, 50/200-day moving averages, beta | 1 hour |
| `AnalystRatings` | Consensus ratings, price targets | 24 hours |
| `Earnings::History` | Historical EPS actuals vs. estimates | 24 hours |
| `Earnings::Trend` | Forward EPS estimates and revenue trends | 24 hours |
| `Financials::Income_Statement::yearly` | Annual income statement | 24 hours |
| `Financials::Income_Statement::quarterly` | Quarterly income statement | 24 hours |
| `Financials::Balance_Sheet::yearly` | Annual balance sheet | 24 hours |
| `Financials::Balance_Sheet::quarterly` | Quarterly balance sheet | 24 hours |
| `Financials::Cash_Flow::yearly` | Annual cash flow statement | 24 hours |
| `Financials::Cash_Flow::quarterly` | Quarterly cash flow statement | 24 hours |

**Example Request — highlights only**

```bash
curl "http://localhost:8000/api/v1/stock/AAPL/fundamental?filter=Highlights"
```

**Example Request — full fundamentals (no filter)**

```bash
curl http://localhost:8000/api/v1/stock/AAPL/fundamental
```

**Cache TTL**: 1 hour – 24 hours (depends on filter)

---

### GET `/stock/{symbol}/news`

Returns recent news articles for a specific stock.

**Path Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | Yes | Stock ticker symbol |

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | No | Number of news items to return (min: 1, max: 1000) |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/stock/AAPL/news?limit=10"
```

**Example Response**

```json
[
  {
    "date": "2025-03-05T14:23:00+00:00",
    "title": "Apple unveils new chip architecture",
    "content": "...",
    "link": "https://...",
    "symbols": ["AAPL.US"],
    "tags": ["Technology", "Hardware"]
  }
]
```

**Cache TTL**: 5 minutes

---

## Calendar Endpoints

### GET `/calendar/economic`

Returns scheduled macroeconomic events (e.g., CPI, Fed meetings, GDP releases) for a date range.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `from` | string | Yes | Start date in `YYYY-MM-DD` format |
| `to` | string | Yes | End date in `YYYY-MM-DD` format |
| `country` | string | No | ISO 3166 2-letter country code to filter events |

**Supported Country Codes**

`US` `GB` `DE` `FR` `JP` `CN` `AU` `CA` `CH` `EU` `IN` `BR` `KR` `MX`

**Example Request**

```bash
curl "http://localhost:8000/api/v1/calendar/economic?from=2025-03-01&to=2025-03-31&country=US"
```

**Cache TTL**: 30 minutes

---

### GET `/calendar/earnings`

Returns the earnings release calendar for all companies in a date range.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `from` | string | Yes | Start date in `YYYY-MM-DD` format |
| `to` | string | Yes | End date in `YYYY-MM-DD` format |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/calendar/earnings?from=2025-04-01&to=2025-04-30"
```

**Cache TTL**: 1 hour

---

### GET `/calendar/earnings/symbol/{symbol}`

Returns upcoming and historical earnings dates for a specific company.

**Path Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | Yes | Stock ticker symbol |

**Example Request**

```bash
curl http://localhost:8000/api/v1/calendar/earnings/symbol/AAPL
```

**Cache TTL**: 1 hour

---

### GET `/calendar/dividends`

Returns all stocks with an ex-dividend date on a specific day.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `date` | string | Yes | Ex-dividend date in `YYYY-MM-DD` format |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/calendar/dividends?date=2025-03-07"
```

**Cache TTL**: 1 hour

---

### GET `/calendar/splits`

Returns scheduled and historical stock splits for a date range.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `from` | string | Yes | Start date in `YYYY-MM-DD` format |
| `to` | string | Yes | End date in `YYYY-MM-DD` format |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/calendar/splits?from=2025-01-01&to=2025-03-31"
```

**Cache TTL**: 1 hour

---

### GET `/calendar/ipo`

Returns the IPO calendar for a date range.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `from` | string | Yes | Start date in `YYYY-MM-DD` format |
| `to` | string | Yes | End date in `YYYY-MM-DD` format |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/calendar/ipo?from=2025-03-01&to=2025-03-31"
```

**Cache TTL**: 1 hour

---

## Market Endpoints

### GET `/market/real-time-quotes`

Returns real-time quotes for a mixed list of symbols across any exchange type in a single call. Accepts symbols with explicit exchange suffixes.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbols` | string | Yes | Comma-separated symbols with exchange suffix (e.g. `TSLA.US,ETH-USD.CC,GC.COMM,GSPC.INDX`) |

**Supported Exchange Suffixes**

| Suffix | Asset Type |
|---|---|
| `.US` | US stocks |
| `.INDX` | Market indices |
| `.COMM` | Commodities |
| `.CC` | Cryptocurrencies |
| `.GBOND` | Government bonds |
| `.FOREX` | Forex pairs |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/market/real-time-quotes?symbols=TSLA.US,ETH-USD.CC,GC.COMM,GSPC.INDX"
```

**Cache TTL**: 15 seconds

---

### GET `/market/intraday`

Returns intraday OHLCV bars for any symbol across any exchange type.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | Yes | Symbol with exchange suffix (e.g. `AAPL.US`, `ETH-USD.CC`) |
| `interval` | string | No | Bar interval: `1m`, `5m`, or `1h` (default: `1h`) |
| `from` | integer | No | Start time as Unix timestamp (UTC) |
| `to` | integer | No | End time as Unix timestamp (UTC) |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/market/intraday?symbol=AAPL.US&interval=5m"
```

**Example Response**

```json
[
  {
    "datetime": "2025-03-05 14:30:00",
    "open": 227.20,
    "high": 228.10,
    "low": 226.90,
    "close": 227.85,
    "volume": 312400
  }
]
```

> Omitting `from`/`to` returns the last 120 days of bars.

**Cache TTL**: 60 seconds

---

### GET `/market/eod`

Returns end-of-day OHLCV bars for any symbol across any exchange type. More flexible than the stock-specific historical endpoint — works for stocks, crypto, indices, commodities, and bonds.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbol` | string | Yes | Symbol with exchange suffix (e.g. `AAPL.US`, `ETH-USD.CC`, `GC.COMM`, `GSPC.INDX`) |
| `from` | string | No | Start date in `YYYY-MM-DD` format |
| `to` | string | No | End date in `YYYY-MM-DD` format |
| `period` | string | No | Bar period: `d` daily, `w` weekly, `m` monthly (default: `d`) |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/market/eod?symbol=ETH-USD.CC&from=2025-01-01&to=2025-03-01&period=w"
```

**Example Response**

```json
[
  {
    "date": "2025-03-01",
    "open": 2200.00,
    "high": 2350.00,
    "low": 2180.00,
    "close": 2310.50,
    "adjusted_close": 2310.50,
    "volume": 18200000
  }
]
```

> Omitting `from`/`to` returns the full available history.

**Cache TTL**: 1 hour

---

### GET `/market/screener`

Returns a filtered and sorted list of stocks matching the given criteria. Useful for building watchlists, screeners, or dashboard widgets.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `sort` | string | Yes | Field to sort results by (see valid values below) |
| `limit` | integer | No | Number of results (min: 1, max: 100, default: 20) |
| `filters` | string | No | URL-encoded JSON array of filter conditions |

**Valid `sort` Values**

| Value | Description |
|---|---|
| `refund_1d_p` | 1-day return % (default order) |
| `refund_1d_p.desc` | Top gainers (descending) |
| `refund_1d_p.asc` | Top losers (ascending) |
| `avgvol_1d` | Average 1-day volume |
| `avgvol_200d` | Average 200-day volume |
| `market_capitalization` | Market cap (default order) |
| `market_capitalization.desc` | Largest companies first |
| `market_capitalization.asc` | Smallest companies first |
| `adjusted_close` | Adjusted closing price |
| `dividend_yield` | Dividend yield |

**Filter Format**

Filters are a JSON array of condition tuples: `[[field, operator, value], ...]`

Supported operators: `=`, `>`, `<`, `>=`, `<=`, `!=`

**Example filter** — US-listed large-cap stocks:
```json
[["exchange","=","US"],["market_capitalization",">","1000000000"]]
```

**Example Request**

```bash
curl "http://localhost:8000/api/v1/market/screener?sort=market_capitalization.desc&limit=10&filters=%5B%5B%22exchange%22%2C%22%3D%22%2C%22US%22%5D%5D"
```

**Cache TTL**: 5 minutes

---

### GET `/market/screener/gainers`

Returns the top gaining stocks by 1-day return percentage. Shortcut for `screener?sort=refund_1d_p.desc`.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | No | Number of results (min: 1, max: 100, default: 20) |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/market/screener/gainers?limit=5"
```

**Cache TTL**: 5 minutes

---

### GET `/market/screener/losers`

Returns the top losing stocks by 1-day return percentage. Shortcut for `screener?sort=refund_1d_p.asc`.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | No | Number of results (min: 1, max: 100, default: 20) |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/market/screener/losers?limit=5"
```

**Cache TTL**: 5 minutes

---

### GET `/market/screener/most-active`

Returns the most actively traded stocks by 1-day average volume.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | No | Number of results (min: 1, max: 100, default: 20) |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/market/screener/most-active?limit=10"
```

**Cache TTL**: 5 minutes

---

### GET `/market/news`

Returns general market news not tied to a specific stock symbol.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `limit` | integer | No | Number of news items (min: 1, max: 100, default: 50) |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/market/news?limit=20"
```

**Cache TTL**: 5 minutes

---

### GET `/market/indices`

Returns the full list of supported market indices with their symbols and display names.

**Example Request**

```bash
curl http://localhost:8000/api/v1/market/indices
```

**Example Response**

```json
[
  { "symbol": "GSPC", "name": "S&P 500" },
  { "symbol": "DJI", "name": "Dow Jones Industrial Average" },
  { "symbol": "IXIC", "name": "Nasdaq Composite" },
  { "symbol": "RUT", "name": "Russell 2000" },
  { "symbol": "FTSE", "name": "FTSE 100" },
  { "symbol": "GDAXI", "name": "DAX" },
  { "symbol": "FCHI", "name": "CAC 40" },
  { "symbol": "STOXX50E", "name": "Euro Stoxx 50" },
  { "symbol": "N225", "name": "Nikkei 225" },
  { "symbol": "HSI", "name": "Hang Seng" },
  { "symbol": "000001", "name": "Shanghai Composite" }
]
```

---

### GET `/market/indices/real-time-quotes`

Returns real-time quote data for one or more market indices. Pass a single symbol to get a JSON object, or multiple comma-separated symbols to get a JSON array.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbols` | string | Yes | Comma-separated index symbols (e.g. `GSPC` or `GSPC,DJI,IXIC`) |

**Example Request — single index**

```bash
curl "http://localhost:8000/api/v1/market/indices/real-time-quotes?symbols=GSPC"
```

**Example Request — multiple indices**

```bash
curl "http://localhost:8000/api/v1/market/indices/real-time-quotes?symbols=GSPC,DJI,IXIC"
```

**Cache TTL**: 30 seconds

---

### GET `/market/indices/{index}/historical-eod`

Returns end-of-day historical price data for a market index.

**Path Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `index` | string | Yes | Index symbol |

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `from` | string | Yes | Start date in `YYYY-MM-DD` format |
| `to` | string | Yes | End date in `YYYY-MM-DD` format |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/market/indices/GSPC/historical-eod?from=2025-01-01&to=2025-03-01"
```

**Cache TTL**: 1 hour

---

### GET `/market/commodities`

Returns the full list of supported commodities with their symbols and display names.

**Example Request**

```bash
curl http://localhost:8000/api/v1/market/commodities
```

**Example Response**

```json
[
  { "symbol": "GC", "name": "Gold" },
  { "symbol": "SI", "name": "Silver" },
  { "symbol": "CL", "name": "Crude Oil (WTI)" },
  { "symbol": "BZ", "name": "Crude Oil (Brent)" },
  { "symbol": "NG", "name": "Natural Gas" },
  { "symbol": "ZW", "name": "Wheat" },
  { "symbol": "ZC", "name": "Corn" }
]
```

**Supported Commodities**

| Category | Symbols |
|---|---|
| Metals | `GC` (Gold), `SI` (Silver), `PL` (Platinum), `PA` (Palladium), `HG` (Copper) |
| Energy | `CL` (Crude Oil WTI), `BZ` (Crude Oil Brent), `NG` (Natural Gas), `HO` (Heating Oil), `RB` (Gasoline) |
| Agriculture | `ZW` (Wheat), `ZC` (Corn), `ZS` (Soybeans), `KC` (Coffee), `SB` (Sugar), `CC` (Cocoa), `CT` (Cotton) |

---

### GET `/market/commodities/real-time-quotes`

Returns real-time quote data for one or more commodities. Pass a single symbol to get a JSON object, or multiple comma-separated symbols to get a JSON array.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbols` | string | Yes | Comma-separated commodity symbols (e.g. `GC` or `GC,SI,CL`) |

**Example Request — single commodity**

```bash
curl "http://localhost:8000/api/v1/market/commodities/real-time-quotes?symbols=GC"
```

**Example Request — multiple commodities**

```bash
curl "http://localhost:8000/api/v1/market/commodities/real-time-quotes?symbols=GC,SI,CL"
```

**Cache TTL**: 30 seconds

---

### GET `/market/crypto`

Returns the full list of supported cryptocurrencies with their symbols and display names.

**Example Request**

```bash
curl http://localhost:8000/api/v1/market/crypto
```

**Example Response**

```json
[
  { "symbol": "BTC-USD", "name": "Bitcoin" },
  { "symbol": "ETH-USD", "name": "Ethereum" },
  { "symbol": "SOL-USD", "name": "Solana" },
  { "symbol": "BNB-USD", "name": "BNB" },
  { "symbol": "XRP-USD", "name": "XRP" },
  { "symbol": "USDC-USD", "name": "USD Coin" },
  { "symbol": "ADA-USD", "name": "Cardano" },
  { "symbol": "AVAX-USD", "name": "Avalanche" },
  { "symbol": "DOGE-USD", "name": "Dogecoin" },
  { "symbol": "TRX-USD", "name": "TRON" }
]
```

---

### GET `/market/crypto/real-time-quotes`

Returns real-time quote data for one or more cryptocurrencies. Pass a single symbol to get a JSON object, or multiple comma-separated symbols to get a JSON array.

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `symbols` | string | Yes | Comma-separated crypto symbols (e.g. `BTC-USD` or `BTC-USD,ETH-USD,SOL-USD`) |

**Example Request — single crypto**

```bash
curl "http://localhost:8000/api/v1/market/crypto/real-time-quotes?symbols=BTC-USD"
```

**Example Request — multiple cryptos**

```bash
curl "http://localhost:8000/api/v1/market/crypto/real-time-quotes?symbols=BTC-USD,ETH-USD,SOL-USD"
```

**Cache TTL**: 15 seconds

---

### GET `/market/bonds`

Returns the full list of supported government bonds with their symbols and display names.

**Example Request**

```bash
curl http://localhost:8000/api/v1/market/bonds
```

**Example Response**

```json
[
  { "symbol": "US1Y", "name": "US 1-Year Treasury" },
  { "symbol": "US2Y", "name": "US 2-Year Treasury" },
  { "symbol": "US5Y", "name": "US 5-Year Treasury" },
  { "symbol": "US10Y", "name": "US 10-Year Treasury" },
  { "symbol": "US30Y", "name": "US 30-Year Treasury" }
]
```

---

### GET `/market/bonds/{bond}/historical-eod`

Returns end-of-day historical data for a government bond.

**Path Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `bond` | string | Yes | Bond symbol (e.g. `US10Y`, `US2Y`) |

**Query Parameters**

| Parameter | Type | Required | Description |
|---|---|---|---|
| `from` | string | No | Start date in `YYYY-MM-DD` format |
| `to` | string | No | End date in `YYYY-MM-DD` format |

**Example Request**

```bash
curl "http://localhost:8000/api/v1/market/bonds/US10Y/historical-eod?from=2025-01-01&to=2025-03-01"
```

> Omitting `from`/`to` returns the full available history (5+ years).

**Cache TTL**: 1 hour

---

## Health

### GET `/health`

Returns the current health status of the API server. Does not require authentication and is not versioned (available at the root, not under `/api/v1`).

**Example Request**

```bash
curl http://localhost:8000/health
```

**Example Response**

```json
{ "status": "ok" }
```

---

## Workflows & Common Use Cases

### Workflow 1 — Build a stock overview page

Fetch all relevant data for a stock detail page in parallel:

```bash
# Real-time price
curl "http://localhost:8000/api/v1/stock/quote?symbols=AAPL"

# Key highlights (market cap, EPS, P/E)
curl "http://localhost:8000/api/v1/stock/AAPL/fundamental?filter=Highlights"

# Analyst ratings
curl "http://localhost:8000/api/v1/stock/AAPL/fundamental?filter=AnalystRatings"

# Latest 10 news items
curl "http://localhost:8000/api/v1/stock/AAPL/news?limit=10"
```

---

### Workflow 2 — Build a market dashboard

```bash
# Major index quotes in one call
curl "http://localhost:8000/api/v1/market/indices/real-time-quotes?symbols=GSPC,DJI,IXIC"

# Top 5 gainers and losers
curl "http://localhost:8000/api/v1/market/screener/gainers?limit=5"
curl "http://localhost:8000/api/v1/market/screener/losers?limit=5"

# Market headlines
curl "http://localhost:8000/api/v1/market/news?limit=10"
```

---

### Workflow 3 — Research an earnings season

```bash
# Upcoming earnings in Q1
curl "http://localhost:8000/api/v1/calendar/earnings?from=2025-04-01&to=2025-04-30"

# Specific company earnings history
curl http://localhost:8000/api/v1/calendar/earnings/symbol/MSFT

# Detailed earnings trend and history
curl "http://localhost:8000/api/v1/stock/MSFT/fundamental?filter=Earnings::History"
curl "http://localhost:8000/api/v1/stock/MSFT/fundamental?filter=Earnings::Trend"
```

---

### Workflow 4 — Screen for large-cap US stocks with high dividend yield

```bash
# Filter: US exchange, market cap > $10B, sorted by dividend yield
curl "http://localhost:8000/api/v1/market/screener?sort=dividend_yield&limit=20&filters=%5B%5B%22exchange%22%2C%22%3D%22%2C%22US%22%5D%2C%5B%22market_capitalization%22%2C%22%3E%22%2C%2210000000000%22%5D%5D"
```

Decoded `filters` value:
```json
[["exchange","=","US"],["market_capitalization",">","10000000000"]]
```

---

### Workflow 5 — Monitor insider trading activity

```bash
# All recent insider transactions
curl http://localhost:8000/api/v1/stock/insider_transactions

# Insider transactions for a specific stock
curl "http://localhost:8000/api/v1/stock/insider_transactions?symbol=NVDA&limit=10"
```

---

### Workflow 6 — Multi-asset real-time dashboard

Fetch quotes for stocks, crypto, indices, and commodities in a single call:

```bash
curl "http://localhost:8000/api/v1/market/real-time-quotes?symbols=TSLA.US,BTC-USD.CC,GC.COMM,GSPC.INDX"
```

---

### Workflow 7 — Crypto portfolio tracker

```bash
# List available cryptos
curl http://localhost:8000/api/v1/market/crypto

# Real-time prices for a portfolio
curl "http://localhost:8000/api/v1/market/crypto/real-time-quotes?symbols=BTC-USD,ETH-USD,SOL-USD"

# Historical EOD for charting
curl "http://localhost:8000/api/v1/market/eod?symbol=BTC-USD.CC&from=2025-01-01&to=2025-03-01"
```

---

### Workflow 8 — Bond yield monitoring

```bash
# List supported bonds
curl http://localhost:8000/api/v1/market/bonds

# Historical yield curve data
curl "http://localhost:8000/api/v1/market/bonds/US2Y/historical-eod?from=2024-01-01&to=2025-01-01"
curl "http://localhost:8000/api/v1/market/bonds/US10Y/historical-eod?from=2024-01-01&to=2025-01-01"
```

---

## Reference: Parameters & Types

### Data Types

| Type | Format | Example |
|---|---|---|
| `string` | UTF-8 text | `"AAPL"` |
| `integer` | Whole number | `50` |
| `date` | ISO 8601 | `"2025-03-01"` |
| `timestamp` | Unix UTC integer | `1741200000` |
| `json_array` | URL-encoded JSON | `%5B%5B%22exchange%22%2C%22%3D%22%2C%22US%22%5D%5D` |

### Common Parameters

| Parameter | Type | Description |
|---|---|---|
| `symbols` | string | Comma-separated tickers. US stocks use bare tickers (`AAPL`); cross-asset endpoints require exchange suffixes (`AAPL.US`) |
| `symbol` | string | Single ticker, used on path-parameter endpoints |
| `from` | date or timestamp | Inclusive start of range. Date string for EOD endpoints; Unix timestamp for intraday |
| `to` | date or timestamp | Inclusive end of range. Date string for EOD endpoints; Unix timestamp for intraday |
| `limit` | integer | Caps the number of results returned |
| `filter` | string | Selects a sub-section of a larger response object (fundamentals) |
| `period` | string | Bar aggregation period — `d` daily, `w` weekly, `m` monthly |
| `interval` | string | Intraday bar size — `1m`, `5m`, `1h` |

### Supported Index Symbols

| Symbol | Index |
|---|---|
| `GSPC` | S&P 500 |
| `DJI` | Dow Jones Industrial Average |
| `IXIC` | Nasdaq Composite |
| `RUT` | Russell 2000 |
| `FTSE` | FTSE 100 |
| `GDAXI` | DAX |
| `FCHI` | CAC 40 |
| `STOXX50E` | Euro Stoxx 50 |
| `N225` | Nikkei 225 |
| `HSI` | Hang Seng |
| `000001` | Shanghai Composite |

### Supported Commodity Symbols

| Symbol | Commodity | Category |
|---|---|---|
| `GC` | Gold | Metals |
| `SI` | Silver | Metals |
| `PL` | Platinum | Metals |
| `PA` | Palladium | Metals |
| `HG` | Copper | Metals |
| `CL` | Crude Oil WTI | Energy |
| `BZ` | Crude Oil Brent | Energy |
| `NG` | Natural Gas | Energy |
| `HO` | Heating Oil | Energy |
| `RB` | Gasoline | Energy |
| `ZW` | Wheat | Agriculture |
| `ZC` | Corn | Agriculture |
| `ZS` | Soybeans | Agriculture |
| `KC` | Coffee | Agriculture |
| `SB` | Sugar | Agriculture |
| `CC` | Cocoa | Agriculture |
| `CT` | Cotton | Agriculture |

### Supported Crypto Symbols

| Symbol | Name |
|---|---|
| `BTC-USD` | Bitcoin |
| `ETH-USD` | Ethereum |
| `SOL-USD` | Solana |
| `BNB-USD` | BNB |
| `XRP-USD` | XRP |
| `USDC-USD` | USD Coin |
| `ADA-USD` | Cardano |
| `AVAX-USD` | Avalanche |
| `DOGE-USD` | Dogecoin |
| `TRX-USD` | TRON |

### Supported Bond Symbols

| Symbol | Name |
|---|---|
| `US1Y` | US 1-Year Treasury |
| `US2Y` | US 2-Year Treasury |
| `US5Y` | US 5-Year Treasury |
| `US10Y` | US 10-Year Treasury |
| `US30Y` | US 30-Year Treasury |

### Supported Economic Calendar Country Codes

| Code | Country / Region |
|---|---|
| `US` | United States |
| `GB` | United Kingdom |
| `DE` | Germany |
| `FR` | France |
| `JP` | Japan |
| `CN` | China |
| `AU` | Australia |
| `CA` | Canada |
| `CH` | Switzerland |
| `EU` | European Union |
| `IN` | India |
| `BR` | Brazil |
| `KR` | South Korea |
| `MX` | Mexico |
