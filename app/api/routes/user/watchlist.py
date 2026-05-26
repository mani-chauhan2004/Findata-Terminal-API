import asyncio
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.paths import PROJECT_ROOT

router = APIRouter(
    prefix="/watchlist",
    tags=["Watchlist"],
)

WATCHLIST_FILE = PROJECT_ROOT / "data" / "watchlist.json"

_lock = asyncio.Lock()


def _read() -> dict:
    if not WATCHLIST_FILE.exists():
        return {}
    with open(WATCHLIST_FILE, "r") as f:
        return json.load(f)


def _write(data: dict) -> None:
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(data, f, indent=2)


class TokensBody(BaseModel):
    tokens: list[str]


@router.post("/{address}", status_code=201)
async def init_address(address: str):
    """Register a new address with an empty watchlist. No-op if it already exists."""
    async with _lock:
        data = _read()
        if address in data:
            return {"address": address, "tokens": data[address]}
        data[address] = []
        _write(data)
    return {"address": address, "tokens": []}


@router.get("/{address}")
async def get_watchlist(address: str):
    """Get the token watchlist for an address."""
    data = _read()
    if address not in data:
        raise HTTPException(status_code=404, detail="Address not found")
    return {"address": address, "tokens": data[address]}


@router.post("/{address}/tokens", status_code=200)
async def add_tokens(address: str, body: TokensBody):
    """Add one or more tokens to an address's watchlist (duplicates are ignored)."""
    async with _lock:
        data = _read()
        if address not in data:
            raise HTTPException(status_code=404, detail="Address not found. Initialize it first via POST /watchlist/{address}")
        existing = set(data[address])
        for token in body.tokens:
            existing.add(token.upper())
        data[address] = sorted(existing)
        _write(data)
    return {"address": address, "tokens": data[address]}


@router.put("/{address}/tokens", status_code=200)
async def replace_tokens(address: str, body: TokensBody):
    """Replace the entire token list for an address."""
    async with _lock:
        data = _read()
        if address not in data:
            raise HTTPException(status_code=404, detail="Address not found. Initialize it first via POST /watchlist/{address}")
        data[address] = sorted({t.upper() for t in body.tokens})
        _write(data)
    return {"address": address, "tokens": data[address]}


@router.delete("/{address}/tokens/{token}", status_code=200)
async def remove_token(address: str, token: str):
    """Remove a single token from an address's watchlist."""
    async with _lock:
        data = _read()
        if address not in data:
            raise HTTPException(status_code=404, detail="Address not found")
        token = token.upper()
        if token not in data[address]:
            raise HTTPException(status_code=404, detail=f"Token {token} not in watchlist")
        data[address].remove(token)
        _write(data)
    return {"address": address, "tokens": data[address]}


@router.delete("/{address}", status_code=200)
async def remove_address(address: str):
    """Remove an address and its entire watchlist."""
    async with _lock:
        data = _read()
        if address not in data:
            raise HTTPException(status_code=404, detail="Address not found")
        del data[address]
        _write(data)
    return {"detail": f"Address {address} removed"}
