"""
api/middleware/auth.py
-----------------------
API Key authentication middleware.
Validates X-API-Key header on all non-public endpoints.

/auth/* routes are explicitly public — JWT auth handles identity there.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from config.settings import settings

# Exact path matches that skip API key check
PUBLIC_PATHS = {
    "/health", "/ready", "/live", "/metrics",
    "/docs", "/redoc", "/openapi.json",
}


def _is_public(path: str) -> bool:
    """Returns True if the request path should skip API key validation."""
    if path in PUBLIC_PATHS:
        return True
    # All /auth/* endpoints are public (JWT handles identity)
    if path.startswith("/auth/"):
        return True
    return False


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if _is_public(request.url.path):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key", "")
        if api_key != settings.RTI_API_KEY:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "unauthorized",
                    "message": "Invalid or missing X-API-Key header",
                    "code": "MISSING_API_KEY",
                },
            )
        return await call_next(request)
