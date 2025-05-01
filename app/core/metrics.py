from prometheus_client import Counter, Histogram, Gauge, Info
import time
from starlette.middleware.base import BaseHTTPMiddleware

# API request metrics
REQUEST_COUNT = Counter(
    'chat_api_requests_total',
    'Total number of requests to the API',
    ['method', 'endpoint', 'status_code']
)

REQUEST_LATENCY = Histogram(
    'chat_api_request_latency_seconds',
    'Request latency in seconds',
    ['method', 'endpoint']
)

# Database metrics
DB_CONNECTION_POOL = Gauge(
    'chat_api_db_pool_size',
    'Database connection pool size',
    ['status']  # 'used', 'idle', 'total'
)

DB_QUERY_LATENCY = Histogram(
    'chat_api_db_query_latency_seconds',
    'Database query latency in seconds',
    ['operation']  # 'select', 'insert', 'update', 'delete'
)

# Cache metrics
CACHE_HIT = Counter(
    'chat_api_cache_hit_total',
    'Total number of cache hits',
    ['cache_type']  # 'redis', 'local'
)

CACHE_MISS = Counter(
    'chat_api_cache_miss_total',
    'Total number of cache misses',
    ['cache_type']  # 'redis', 'local'
)

# WebSocket metrics
WEBSOCKET_CONNECTIONS = Gauge(
    'chat_api_websocket_connections',
    'Current number of active WebSocket connections',
    ['room_id']
)

WEBSOCKET_MESSAGES = Counter(
    'chat_api_websocket_messages_total',
    'Total number of WebSocket messages',
    ['direction']  # 'incoming', 'outgoing'
)

# System info
API_INFO = Info(
    'chat_api',
    'Information about the Chat API'
)

class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        # One-time setup can go here

    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)

        # Skip metrics endpoint itself to avoid recursion
        if request.url.path != "/metrics":
            # Record request latency
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(time.time() - start_time)

            # Count request
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code
            ).inc()

        return response


def setup_metrics(app_version: str):
    """Initialize metrics with application info"""
    API_INFO.info({
        'version': app_version,
        'python_version': '3.9'
    })
