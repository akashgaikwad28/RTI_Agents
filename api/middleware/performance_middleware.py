"""
api/middleware/performance_middleware.py
-----------------------------------------
Tracks slow requests and updates Prometheus request metrics.
"""

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from observability.metrics import rti_requests_total
from observability.telemetry import telemetry
from observability.telemetry_models import Outcome, LogLevel

SLOW_REQUEST_THRESHOLD_MS = 5000.0  # 5 seconds

class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Track basic metrics
        path = request.url.path
        # Extremely simplified categorization for prometheus metrics
        intent = "api"
        if "/rag" in path: intent = "rag"
        elif "/rti" in path: intent = "rti"
        
        rti_requests_total.labels(intent=intent).inc()
        
        # Track slow requests
        if latency_ms > SLOW_REQUEST_THRESHOLD_MS:
            telemetry.log_graph_event(  # Using graph event broadly for system performance
                event="slow_http_request",
                operation="performance_monitoring",
                outcome=Outcome.DEGRADED,
                execution_time_ms=latency_ms,
                level=LogLevel.WARNING
            )
            
        return response
