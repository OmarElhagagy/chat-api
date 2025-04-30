from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import time
from ..db.redis_cache import cache
from ..core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # paths to skip rate limiting for
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host

        # Create rate limit key
        rate_key = f"rate_limit: {client_ip}"

        # Get current count
        current = cache.client.get(rate_key)

        if current is None:
            # First request in this period
            cache.client.setex(rate_key, 60, 1) # 60 sec expiry
        elif int(current) >= settings.RATE_LIMIT_PER_MINUTE:
            # Rate limit exceeded
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        else:
            cache.client.incr(rate_key) # Increment request count


        # process the request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # processing time header
        response.headers["X-Process-Time"] = str(process_time)

        return response
