from datetime import datetime, timezone
from fastapi import Header, HTTPException, Request
from app.core.config import settings
from app.core.database import get_db

ROUTER_PATH_PREFIXES: dict[str, str] = {
    "stock": "/stock",
    "market": "/market",
    "calendar": "/calendar",
    "crypto": "/market/crypto",
}


async def verify_api_key(request: Request, x_api_key: str | None = Header(None)) -> None:
    if x_api_key is None:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "unauthenticated",
                "message": "No API key was provided. Pass your key via the X-Api-Key request header.",
            },
        )
    async with get_db() as db:
        async with db.execute(
            "SELECT created_at, ttl, router FROM api_keys WHERE key = ?", (x_api_key,)
        ) as cursor:
            row = await cursor.fetchone()
    if row is None:
        raise HTTPException(
            status_code=403,
            detail={
                "status": "unauthorized",
                "message": "The API key provided is invalid or has been revoked.",
            },
        )

    if row["ttl"] is not None:
        created_at = datetime.fromisoformat(row["created_at"])
        elapsed = (datetime.now(timezone.utc) - created_at).total_seconds()
        if elapsed > row["ttl"]:
            raise HTTPException(
                status_code=403,
                detail={
                    "status": "unauthorized",
                    "message": "The API key provided has expired. Please request a new key.",
                },
            )

    allowed_routers = {r.strip() for r in row["router"].split(",")}
    if "all" not in allowed_routers:
        path = request.url.path
        if not any(path.startswith(ROUTER_PATH_PREFIXES[r]) for r in allowed_routers if r in ROUTER_PATH_PREFIXES):
            raise HTTPException(
                status_code=403,
                detail={
                    "status": "unauthorized",
                    "message": f"Your API key does not have permission to access this endpoint.",
                },
            )


async def verify_admin_key(x_api_key: str | None = Header(None)) -> None:
    if x_api_key is None:
        raise HTTPException(
            status_code=401,
            detail={
                "status": "unauthenticated",
                "message": "No admin key was provided. Pass your key via the X-Api-Key request header.",
            },
        )
    if x_api_key != settings.ADMIN_KEY:
        raise HTTPException(
            status_code=403,
            detail={
                "status": "unauthorized",
                "message": "The admin key provided is invalid.",
            },
        )
