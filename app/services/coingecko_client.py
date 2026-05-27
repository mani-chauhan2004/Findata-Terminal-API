import json
import httpx
from app.core.coingecko_http_client import get_coingecko_client
from app.core.exceptions import UpstreamAPIError, UpstreamParseError


def _parse_response(response, empty_default=None):
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise UpstreamAPIError(
            status_code=e.response.status_code,
            endpoint=str(e.request.url.path),
        ) from None
    text = response.text.strip()
    if not text:
        return empty_default if empty_default is not None else {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        raise UpstreamParseError() from None


class CoinGeckoClient:
    async def get_market_cap_data(self, ids: str, order: str) -> list:
        client = await get_coingecko_client()
        params = {
            "vs_currency": "usd",
            "ids": ids,
            "order": order,
        }
        response = await client.get("/api/v3/coins/markets", params=params)
        return _parse_response(response, empty_default=[])

    async def get_token_price_data(
        self,
        platform: str,
        contract_addresses: str,
        vs_currencies: str = "usd",
        include_24hr_vol: bool = False,
        include_24hr_change: bool = False,
    ) -> dict:
        client = await get_coingecko_client()
        params: dict = {
            "contract_addresses": contract_addresses,
            "vs_currencies": vs_currencies,
            "include_market_cap": "true",
        }
        if include_24hr_vol:
            params["include_24hr_vol"] = "true"
        if include_24hr_change:
            params["include_24hr_change"] = "true"
        response = await client.get(f"/api/v3/simple/token_price/{platform}", params=params)
        return _parse_response(response, empty_default={})
