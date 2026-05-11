import secrets
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from app.core.database import get_db
from app.core.dependencies import verify_admin_key


router = APIRouter(
    prefix="/admin/keys",
    tags=["Admin"],
    dependencies=[Depends(verify_admin_key)],
)

VALID_ROUTERS = {"all", "stock", "market", "calendar", "crypto"}


class CreateKeyRequest(BaseModel):
    user: str
    ttl: int | None = None
    router: str = "all"

    @field_validator("router")
    @classmethod
    def validate_router(cls, v: str) -> str:
        parts = {r.strip() for r in v.split(",")}
        invalid = parts - VALID_ROUTERS
        if invalid:
            raise ValueError(f"Invalid router(s): {invalid}. Valid options: {VALID_ROUTERS}")
        return ",".join(sorted(parts))


@router.post("/")
async def create_key(body: CreateKeyRequest):
    key = f"rtb_{secrets.token_urlsafe(32)}"
    created_at = datetime.now(timezone.utc).isoformat()
    async with get_db() as db:
        await db.execute(
            "INSERT INTO api_keys (key, user, created_at, ttl, router) VALUES (?, ?, ?, ?, ?)",
            (key, body.user, created_at, body.ttl, body.router),
        )
        await db.commit()
    return {
        "key": key,
        "user": body.user,
        "created_at": created_at,
        "ttl": body.ttl,
        "router": body.router,
    }


@router.get("/")
async def list_keys():
    async with get_db() as db:
        async with db.execute(
            "SELECT key, user, created_at, ttl, router FROM api_keys ORDER BY created_at DESC"
        ) as cursor:
            rows = await cursor.fetchall()
    return [dict(row) for row in rows]


@router.delete("/{key}")
async def revoke_key(key: str):
    async with get_db() as db:
        async with db.execute(
            "DELETE FROM api_keys WHERE key = ?", (key,)
        ) as cursor:
            await db.commit()
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Key not found")
    return {"detail": "Key revoked"}
