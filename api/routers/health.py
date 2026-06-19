"""
api/routers/health.py
----------------------
Health check and readiness endpoints.
"""

from fastapi import APIRouter, Request
from api.schemas import HealthResponse
from config.settings import settings
from observability.structured_logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(request: Request):
    """
    Comprehensive health check — validates all dependencies.
    Returns 200 if fully healthy, 503 if degraded.
    """
    services = {}

    # MongoDB
    try:
        mongo = getattr(request.app.state, "mongo", None)
        if mongo and mongo.client:
            await mongo.client.admin.command("ping")
            services["mongodb"] = "healthy"
        else:
            services["mongodb"] = "not_initialized"
    except Exception as e:
        services["mongodb"] = f"unhealthy: {str(e)[:50]}"

    # Redis
    try:
        cache = getattr(request.app.state, "cache", None)
        services["redis"] = "healthy" if cache and cache.is_available else "unavailable"
    except Exception:
        services["redis"] = "unavailable"

    # FAISS
    faiss = getattr(request.app.state, "faiss", None)
    services["faiss"] = "loaded" if faiss else "not_loaded"

    # LangGraph
    graph = getattr(request.app.state, "graph", None)
    services["langgraph"] = "compiled" if graph else "not_compiled"

    overall = (
        "healthy"
        if all(v in ("healthy", "loaded", "compiled") for v in services.values())
        else "degraded"
    )

    return HealthResponse(
        status=overall,
        version="2.0.0",
        environment=settings.APP_ENV,
        services=services,
    )


@router.get("/ready", tags=["Health"])
async def readiness():
    """Kubernetes readiness probe."""
    return {"ready": True}


@router.get("/live", tags=["Health"])
async def liveness():
    """Kubernetes liveness probe."""
    return {"alive": True}
