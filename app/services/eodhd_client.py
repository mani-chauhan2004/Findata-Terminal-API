import json
from app.core.http_client import get_client


def _parse_response(response, empty_default=None):
    response.raise_for_status()
    text = response.text.strip()
    if not text:
        return empty_default if empty_default is not None else {}
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid response from API: {e}") from e


class EodhdClient:
    async def get_fundamentals_data(self, symbol: str, filter: str | None = None) -> any:
        client = await get_client()
        params = {}
        if filter is not None:
            params["filter"] = filter
        response = await client.get(
            f"/api/fundamentals/{symbol}.US",
            params=params,
        )
        return _parse_response(response, empty_default={})
    
    async def get_earnings_calendar_data(self, symbol: str | None = None, from_date: str | None = None, to_date: str | None = None) -> any:
        client = await get_client()
        params = {}
        if symbol is not None:
            params["symbols"] = f"{symbol}.US"
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        response = await client.get(
            f"/api/calendar/earnings",
            params=params,
        )
        return _parse_response(response, empty_default=[])

    async def get_dividend_history_data(self, symbol: str) -> any:
        client = await get_client()
        response = await client.get(
            f"/api/div/{symbol}.US",
        )
        return _parse_response(response, empty_default=[])

    async def get_hisorical_eod_data(self, symbol: str, from_date: str | None = None, to_date: str | None = None) -> any:
        client = await get_client()
        params = {}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        response = await client.get(
            f"/api/eod/{symbol}.US",
            params=params,
        )
        return _parse_response(response, empty_default=[])

    async def get_intraday_data(self, symbol: str, interval: str | None = None, from_timestamp: int | None = None, to_timestamp: int | None = None) -> any:
        client = await get_client()
        params = {}
        if interval is not None:
            params["interval"] = interval
        if from_timestamp is not None:
            params["from"] = from_timestamp
        if to_timestamp is not None:
            params["to"] = to_timestamp
        response = await client.get(f"/api/intraday/{symbol}", params=params)
        return _parse_response(response, empty_default=[])

    async def get_generic_eod_data(self, symbol: str, from_date: str | None = None, to_date: str | None = None, period: str | None = None) -> any:
        client = await get_client()
        params = {}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        if period is not None:
            params["period"] = period
        response = await client.get(f"/api/eod/{symbol}", params=params)
        return _parse_response(response, empty_default=[])

    async def get_mixed_real_time_quotes_data(self, symbols: list[str]) -> any:
        client = await get_client()
        primary, *extra = symbols
        params = {"s": ",".join(extra)} if extra else {}
        response = await client.get(f"/api/real-time/{primary}", params=params)
        return _parse_response(response, empty_default=[] if extra else {})

    async def get_real_time_quote_data(self, symbols: list[str]) -> any:
        client = await get_client()
        primary, *extra = symbols
        params = {"s": ",".join(f"{s}.US" for s in extra)} if extra else {}
        response = await client.get(f"/api/real-time/{primary}.US", params=params)
        return _parse_response(response, empty_default=[] if extra else {})
    
    async def get_us_quote_delayed_data(self, symbol: str | None = None) -> any:
        client = await get_client()
        params = {}
        if symbol is not None:
            params["s"] = f"{symbol}.US"
        response = await client.get(
            f"/api/us-quote-delayed",
            params=params,
        )
        return _parse_response(response, empty_default={})

    async def get_insider_transactions_data(self, symbol: str | None = None, limit: int | None = None) -> any:
        client = await get_client()
        params = {}
        if symbol is not None:
            params["code"] = f"{symbol}.US"
        if limit is not None:
            params["limit"] = limit
        response = await client.get(
            f"/api/insider-transactions",
            params=params
        )
        return _parse_response(response, empty_default=[])

    async def get_news_data(self, symbol: str | None = None, limit: int | None = None) -> any:
        client = await get_client()
        params = {}
        if symbol is not None:
            params["s"] = f"{symbol}.US"
        if limit is not None:
            params["limit"] = limit
        response = await client.get(
            f"/api/news",
            params=params
        )
        return _parse_response(response, empty_default=[])
    
    async def get_index_based_real_time_quotes_data(self, symbols: list[str]) -> any:
        client = await get_client()
        primary, *extra = symbols
        params = {"s": ",".join(f"{s}.INDX" for s in extra)} if extra else {}
        response = await client.get(f"/api/real-time/{primary}.INDX", params=params)
        return _parse_response(response, empty_default=[] if extra else {})
    
    async def get_index_based_historical_eod_data(self, index: str, from_date: str | None = None, to_date: str | None = None) -> any:
        client = await get_client()
        params = {}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        response = await client.get(
            f"/api/eod/{index}.INDX",
            params=params
        )
        return _parse_response(response, empty_default=[])

    async def get_bond_historical_eod_data(self, bond: str, from_date: str | None = None, to_date: str | None = None) -> any:
        client = await get_client()
        params = {}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        response = await client.get(
            f"/api/eod/{bond}.GBOND",
            params=params
        )
        return _parse_response(response, empty_default=[])

    async def get_commodity_based_real_time_quotes_data(self, symbols: list[str]) -> any:
        client = await get_client()
        primary, *extra = symbols
        params = {"s": ",".join(f"{s}.COMM" for s in extra)} if extra else {}
        response = await client.get(f"/api/real-time/{primary}.COMM", params=params)
        return _parse_response(response, empty_default=[] if extra else {})

    async def get_crypto_real_time_quotes_data(self, symbols: list[str]) -> any:
        client = await get_client()
        primary, *extra = symbols
        params = {"s": ",".join(f"{s}.CC" for s in extra)} if extra else {}
        response = await client.get(f"/api/real-time/{primary}.CC", params=params)
        return _parse_response(response, empty_default=[] if extra else {})

    async def get_screener_data(self, sort: str | None = None, limit: int | None = None, filters: list[list[str]] | None = None) -> any:
        client = await get_client()
        params = {}
        if sort is not None:
            params["sort"] = sort
        if limit is not None:
            params["limit"] = limit
        if filters is not None:
            params["filters"] = json.dumps(filters)
        response = await client.get(
            f"/api/screener",
            params=params,
        )
        return _parse_response(response, empty_default=[])

    async def get_ipo_calendar_data(self, from_date: str | None = None, to_date: str | None = None) -> any:
        client = await get_client()
        params = {}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        response = await client.get(
            f"/api/calendar/ipos",
            params=params,
        )
        return _parse_response(response, empty_default=[])

    async def get_split_calendar_data(self, from_date: str | None = None, to_date: str | None = None) -> any:
        client = await get_client()
        params = {}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        response = await client.get(
            f"/api/calendar/splits",
            params=params,
        )
        return _parse_response(response, empty_default=[])
    
    async def get_dividend_calendar_data(self, symbol: str | None = None, from_date: str | None = None, to_date: str | None = None, date_eq: str | None = None) -> any:
        client = await get_client()
        params = {}
        if from_date is not None:
            params["filter[date_from]"] = from_date
        if to_date is not None:
            params["filter[date_to]"] = to_date
        if symbol is None and date_eq is None:
            raise ValueError("Either symbol or date_eq must be provided")
        if symbol is not None:
            params["filter[symbol]"] = f"{symbol}.US"
        elif date_eq is not None:
            params["filter[date_eq]"] = date_eq
        response = await client.get(
            f"/api/calendar/dividends",
            params=params,
        )
        return _parse_response(response, empty_default=[])

    async def get_economic_events_data(self, from_date: str | None = None, to_date: str | None = None) -> any:
        client = await get_client()
        params = {}
        if from_date is not None:
            params["from"] = from_date
        if to_date is not None:
            params["to"] = to_date
        response = await client.get(
            f"/api/economic-events",
            params=params,
        )
        return _parse_response(response, empty_default=[])

    

    

    
    

