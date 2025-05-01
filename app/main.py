from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from contextlib import asynccontextmanager
import logging
import uvicorn
from .api.auth import router as auth_router
from .api.chat import router as chat_router
from .api.websocket import router as websocket_router
from .api.middleware import RateLimitMiddleware
from .core.metrics import setup_metrics, MetricsMiddleware
from .core.config import settings
from .db.database import db
from .db.redis_cache import cache

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    logger.info("Connecting to database...")
    await db.connect()
    logger.info("Database connection established")
    
    try:
        cache.client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
    yield  # Server runs here
    # Shutdown code
    logger.info("Closing database connection...")
    await db.disconnect()
    logger.info("Database connection closed")

# Create single FastAPI app with all parameters
app = FastAPI(
    title="Scalable Chat API",
    description="A scalable chat API with load balancing and caching",
    version="1.0.0",
    lifespan=lifespan
)

# Setup metrics
setup_metrics("1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production will be replaced with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# metrics middleware
app.add_middleware(MetricsMiddleware)

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include all routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(websocket_router, tags=["WebSocket"])

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    db_status = False
    redis_status = False
    
    # Check database connection
    try:
        if db.pool:
            async with db.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                db_status = True
    except Exception:
        pass
    
    # Check Redis connection
    try:
        cache.client.ping()
        redis_status = True
    except Exception:
        pass
    
    status = "healthy" if db_status and redis_status else "unhealthy"
    
    return {
        "status": status,
        "database": "connected" if db_status else "disconnected",
        "cache": "connected" if redis_status else "disconnected"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # Set to False in production
        workers=settings.WORKERS,
    )
