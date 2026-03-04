import httpx
from app.core.config import settings

_client : httpx.AsyncClient | None = None

async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=settings.EODHD_API_BASE_URL.rstrip("/"),
            params={"api_token": settings.EODHD_API_KEY, "fmt": "json"},
            timeout=httpx.Timeout(10.0, connect=10.0),
        )
    return _client

async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None