from re import A
import httpx
from app.core.config import settings
from app.core.http_client import get_client

class EodhdClient:
    async def get_fundamentals_data(self, symbol: str, filter: str = "") -> any:
        client = await get_client()
        response = await client.get(
            f"/api/fundamentals/{symbol}.US",
            params={
                "filter": filter,
            }
        )
        return response.json()
    
    async def get_earnings_calendar_data(self, symbol: str) -> any:
        client = await get_client()
        response = await client.get(
            f"/api/calendar/earnings?symbol={symbol}.US",
        )
        return response.json()

    async def get_dividend_history_data(self, symbol: str) -> any:
        client = await get_client()
        response = client.get(
            f"/api/div/{symbol}.US",
        )
        return response.json()

    async def get_hisorical_eod_data(self, symbol: str, from_date: str, to_date: str) -> any:
        client = await get_client()
        response = client.get(
            f"/api/eod/{symbol}.US",
            params={
                "from": from_date,
                "to": to_date,
            }
        )
        return response.json()

    async def get_real_time_quote_data(self, symbol: str) -> any:
        client = await get_client()
        response = client.get(
            f"/api/real-time/{symbol}.US",
        )
        return response.json()
    
    async def get_us_quote_delayed_data(self, symbol: str) -> any: 
        client = await get_client()
        response = client.get(
            f"/api/us-quote-delayed",
            params={
                "s": f"{symbol}.US",
            }
        )
        return response.json()

    async def get_insider_transactions_data(self, symbol: str, limit: int = 100) -> any:
        client = await get_client()
        response = await client.get(
            f"/api/insider-transactions",
            params={
                "code": f"{symbol}.US",
                "limit": limit,
            }
        )
        return response.json()

    async def get_news_data(self, symbol: str, limit: int = 100) -> any:
        client = await get_client()
        response = await client.get(
            f"/api/news",
            params={
                "s": f"{symbol}.US",
                "limit": limit,
            }
        )
        return response.json()
    
    async def get_index_based_real_time_quotes_data(self, index: str) -> any:
        client = await get_client()
        response = await client.get(
            f"/api/real-time/{index}.INDX"
        )
        return response.json()
    
    async def get_index_based_historical_eod_data(self, index: str, from_date: str, to_date: str) -> any:
        client = await get_client()
        response = await client.get(
            f"/api/eod/{index}.INDX",
            params={
                "from": from_date,
                "to": to_date,
            }
        )
        return response.json()

    async def get_commodity_based_real_time_quotes_data(self, commodity: str) -> any:
        client = await get_client()
        response = await client.get(
            f"/api/real-time/{commodity}.COMM"
        )
        return response.json()

    async def get_screener_data(self, sort: str, limit: int, filters: list[list[str]]) -> any:
        client = await get_client()
        response = await client.get(
            f"/api/screener",
            params={
                "sort": sort,
                "limit": limit,
                "filters": filters,
            }
        )
        return response.json()

    async def get_ipo_calendar_data(self, from_date: str, to_date: str) -> any:
        client = await get_client()
        response = await client.get(
            f"/api/calendar/ipos",
            params={
                "from": from_date,
                "to": to_date,
            }
        )
        return response.json()

    async def get_split_calendar_data(self, from_date: str, to_date: str) -> any:
        client = await get_client()
        response = await client.get(
            f"/api/calendar/splits",
            params={
                "from": from_date,
                "to": to_date,
            }
        )
        return response.json()
    
    async def get_dividend_calendar_data(self, from_date: str, to_date: str) -> any:
        client = await get_client()
        response = await client.get(
            f"/api/calendar/dividends",
            params={
                "from": from_date,
                "to": to_date,
            }
        )
        return response.json()

    async def get_economic_events_data(self, from_date: str, to_date: str) -> any:
        client = await get_client()
        response = await client.get(
            f"/api/economic-events",
            params={
                "from": from_date,
                "to": to_date,
            }
        )
        return response.json()

    

    

    
    

