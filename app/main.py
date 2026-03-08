import sys
import logging.config
import json
import atexit
import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.core.paths import PROJECT_ROOT
from contextlib import asynccontextmanager
from app.api.router import router
from app.core.redis_client import close_redis
from app.core.http_client import close_client
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
    logger.info("Starting the application")
    yield
    logger.info("Stopping the application")
    await close_redis()
    await close_client()


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    description="Terminal API",
    docs_url="/docs" if settings.ENVIRONMENT == "local" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "local" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT == "local" else None,
)

app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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