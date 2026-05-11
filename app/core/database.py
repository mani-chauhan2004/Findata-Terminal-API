import aiosqlite
from contextlib import asynccontextmanager
from app.core.paths import PROJECT_ROOT

DB_PATH = PROJECT_ROOT / "keys.db"


@asynccontextmanager
async def get_db():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def init_db() -> None:
    async with get_db() as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                key TEXT PRIMARY KEY,
                user TEXT NOT NULL,
                created_at TEXT NOT NULL,
                ttl INTEGER,
                router TEXT NOT NULL DEFAULT 'all'
            )
        """)
        await db.commit()
