"""
api/middleware/request_logging.py
----------------------------------
Logs HTTP requests cleanly using the new JSON telemetry pipeline.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from observability.telemetry_models import BaseTelemetryEvent, Component, Outcome, LogLevel
from observability.logger import get_logger

logger = get_logger("http")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            latency_ms = (time.time() - start_time) * 1000
            
            # Use raw logger here since this is raw HTTP access, not domain telemetry
            status_code = response.status_code
            outcome = Outcome.SUCCESS.value if status_code < 400 else Outcome.FAILURE.value
            level = "INFO" if status_code < 500 else "ERROR"
            
            logger.log(getattr(logging, level, logging.INFO), f"{request.method} {request.url.path}", extra={
                "event": "http_request_completed",
                "component": Component.API.value,
                "operation": "http_request",
                "outcome": outcome,
                "http_method": request.method,
                "http_path": request.url.path,
                "status_code": status_code,
                "latency_ms": latency_ms,
                "client_ip": request.client.host if request.client else "unknown"
            })
            
            return response
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            
            logger.error(f"HTTP Request failed: {str(e)}", extra={
                "event": "http_request_failed",
                "component": Component.API.value,
                "operation": "http_request",
                "outcome": Outcome.FAILURE.value,
                "http_method": request.method,
                "http_path": request.url.path,
                "latency_ms": latency_ms,
                "error": str(e)
            })
            raise e

import logging
