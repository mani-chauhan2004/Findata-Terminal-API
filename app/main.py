import sys
import logging.config
import json
import atexit
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.paths import PROJECT_ROOT
from contextlib import asynccontextmanager
from app.api.router import router
from app.api.routes.admin import keys as admin_keys
from app.api.routes.admin import cache as admin_cache
from app.core.redis_client import close_redis
from app.core.http_client import close_client
from app.core.coingecko_http_client import close_coingecko_client
from app.core.database import init_db
from app.core.exceptions import UpstreamAPIError, UpstreamParseError
from fastapi.middleware.cors import CORSMiddleware

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger("terminal")

def setup_logging():
    config_file = PROJECT_ROOT / "app" / "logging" / "config" / "config.json"
    with open(config_file, "r") as f:
        config = json.load(f)
    # Ensure log file directory exists (RotatingFileHandler does not create it)
    for name, handler_cfg in config.get("handlers", {}).items():
        if "filename" in handler_cfg:
            log_path = PROJECT_ROOT / handler_cfg["filename"]
            log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    await init_db()
    logger.info("Starting the application")
    yield
    logger.info("Stopping the application")
    await close_redis()
    await close_client()
    await close_coingecko_client()


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    description="Terminal API",
    docs_url="/docs" if settings.ENVIRONMENT == "local" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "local" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT == "local" else None,
)

app.include_router(router)
app.include_router(admin_keys.router)
app.include_router(admin_cache.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(UpstreamAPIError)
async def upstream_api_error_handler(request: Request, exc: UpstreamAPIError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(UpstreamParseError)
async def upstream_parse_error_handler(request: Request, exc: UpstreamParseError):
    return JSONResponse(
        status_code=502,
        content={"error": exc.detail},
    )

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    logger.info(f"🚀 Starting server on {settings.HOST}:{settings.PORT}")
    try:
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.ENVIRONMENT == "local",
            access_log=True
        )
    except Exception as e:
        logger.error(f"❌ Error starting server: {e}")
        raise