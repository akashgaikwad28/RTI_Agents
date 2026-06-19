"""
api/middleware/rate_limiter.py
-------------------------------
Sliding window rate limiter using in-memory dict.
Limits requests per API key (60/min) and per IP (20/min).
"""

import time
from collections import defaultdict, deque
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from config.settings import settings
from observability.structured_logger import get_logger

logger = get_logger(__name__)

PUBLIC_PATHS = {"/health", "/ready", "/live", "/metrics", "/docs", "/redoc", "/openapi.json"}

# In-memory sliding windows: {key: deque of timestamps}
_windows: dict[str, deque] = defaultdict(deque)


def _rate_limiter_enabled() -> bool:
    # Prevent local/test automation from being throttled during bursts.
    # Keep production behavior intact.
    return settings.APP_ENV not in {"development", "test"}



class RateLimiterMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        if not _rate_limiter_enabled():
            return await call_next(request)

        now = time.time()

        window = 60.0  # 1 minute window

        # ── Per API key limit ─────────────────────────────────────
        api_key = request.headers.get("X-API-Key", "anonymous")
        key_window = _windows[f"key:{api_key}"]
        while key_window and now - key_window[0] > window:
            key_window.popleft()
        if len(key_window) >= settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(f"[RateLimit] API key rate limit exceeded: {api_key[:12]}")
            return JSONResponse(
                status_code=429,
                content={"error": "rate_limited", "message": "Too many requests. Try again in 60s."},
                headers={"Retry-After": "60"},
            )
        key_window.append(now)

        # ── Per IP limit ──────────────────────────────────────────
        client_ip = request.client.host if request.client else "unknown"
        ip_window = _windows[f"ip:{client_ip}"]
        while ip_window and now - ip_window[0] > window:
            ip_window.popleft()
        if len(ip_window) >= settings.RATE_LIMIT_PER_IP:
            logger.warning(f"[RateLimit] IP rate limit exceeded: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={"error": "rate_limited", "message": "IP rate limit exceeded."},
                headers={"Retry-After": "60"},
            )
        ip_window.append(now)

        return await call_next(request)
