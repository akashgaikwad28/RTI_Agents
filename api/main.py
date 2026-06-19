"""
api/main.py
-----------
Production FastAPI application for RTI-Agent.
Handles startup/shutdown lifecycle, middleware, and routing.
"""

import uuid
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from sse_starlette.sse import EventSourceResponse

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from api.routers import rti, status, health, stream, rag, governance, tools, multilingual, eval
from api.routers.auth import router as auth_router, seed_admin_user
from api.middleware.auth import APIKeyMiddleware
from api.middleware.rate_limiter import RateLimiterMiddleware
from api.middleware.request_id import RequestIDMiddleware
from graph.graph_builder import get_graph
from mcp_clients.mongo_client import get_mongo_client
from rag.vectorstore.semantic_cache import get_semantic_cache
from rag.vectorstore.faiss_store import get_faiss_store
from observability.tracing import setup_tracing
from observability.telemetry import telemetry
from observability.logger import get_logger
from observability.performance_monitor import start_performance_monitors
from config.settings import settings

logger = get_logger("api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: initialize all singletons on startup,
    clean up on shutdown.
    """
    logger.info("🚀 RTI-Agent starting up...", extra={"event": "startup", "component": "api", "operation": "startup"})

    # ── LangSmith tracing ─────────────────────────────────────────
    setup_tracing()
    
    # ── Performance Monitoring ────────────────────────────────────
    await start_performance_monitors()

    postgres_context = None
    mongo = None

    try:
        # ── MongoDB (async motor) ─────────────────────────────────────
        # Do not hard-fail startup: tests and evaluation endpoints should work
        # even when MongoDB is temporarily unavailable.
        try:
            mongo = await get_mongo_client()
            app.state.mongo = mongo
            logger.info("✅ MongoDB connected")
        except Exception as e:
            app.state.mongo = None
            logger.error(f"[MongoDB] Connection failed during startup: {e}")

        # ── Redis semantic cache ──────────────────────────────────────
        try:
            cache = await get_semantic_cache()
            app.state.cache = cache
            logger.info(f"✅ Redis cache: {'connected' if cache.is_available else 'unavailable (degraded mode)'}")
        except Exception as cache_err:
            logger.error(f"[Redis Cache] Failed to initialize semantic cache: {cache_err}. Falling back to degraded mode.")
            class DegradedCache:
                @property
                def is_available(self):
                    return False
                async def get(self, key):
                    return None
                async def set(self, key, value, ttl=None):
                    pass
                async def delete(self, key):
                    pass
            app.state.cache = DegradedCache()

        # ── FAISS vector store ────────────────────────────────────────
        faiss_store = get_faiss_store()
        app.state.faiss = faiss_store
        if faiss_store:
            logger.info("✅ FAISS index loaded")
        else:
            logger.warning("⚠️  FAISS index not found — run ingestion pipeline first")

        from tools.base.tool_registry import get_tool_registry
        app.state.tool_registry = get_tool_registry()
        logger.info("✅ Tool registry initialized")

        # ── Seed admin user ───────────────────────────────────────────
        await seed_admin_user()

        # ── Compile LangGraph ─────────────────────────────────────────
        if settings.CHECKPOINTER_TYPE == "postgres" and settings.POSTGRES_CHECKPOINTER_URL:
            from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
            from graph.graph_builder import lazy_checkpointer
            logger.info("📡 Connecting to Neon PostgreSQL checkpointer...")
            postgres_context = AsyncPostgresSaver.from_conn_string(settings.POSTGRES_CHECKPOINTER_URL)
            saver = await postgres_context.__aenter__()
            app.state.postgres_context = postgres_context
            await saver.setup()
            lazy_checkpointer.set_delegate(saver)
            lazy_checkpointer.set_conn_string(settings.POSTGRES_CHECKPOINTER_URL)
            lazy_checkpointer.set_context(postgres_context)
            logger.info("✅ Neon PostgreSQL checkpointer connected and schema verified")

        graph = get_graph(enable_hitl=settings.HUMAN_APPROVAL_REQUIRED)
        app.state.graph = graph
        logger.info("✅ LangGraph compiled")

        logger.info(f"🟢 RTI-Agent ready on port {settings.PORT} [{settings.APP_ENV}]")

        yield  # ← Application runs here

    except Exception as startup_err:
        logger.critical(f"❌ Server startup failed: {startup_err}")
        # Clean up any resources entered so far
        if postgres_context is not None:
            logger.info("Cleaning up PostgreSQL checkpointer connection due to startup failure...")
            try:
                await postgres_context.__aexit__(None, None, None)
            except Exception as pg_cleanup_err:
                logger.error(f"Error during Postgres cleanup on startup failure: {pg_cleanup_err}")
        if mongo is not None:
            logger.info("Cleaning up MongoDB connection due to startup failure...")
            try:
                await mongo.close()
            except Exception as mongo_cleanup_err:
                logger.error(f"Error during MongoDB cleanup on startup failure: {mongo_cleanup_err}")
        raise startup_err

    # ── Shutdown ──────────────────────────────────────────────────
    logger.info("🔴 RTI-Agent shutting down...")
    if hasattr(app.state, "mongo") and app.state.mongo is not None:
        try:
            await app.state.mongo.close()
            logger.info("✅ MongoDB connection closed")
        except Exception as mongo_close_err:
            logger.error(f"Error closing MongoDB connection: {mongo_close_err}")
            
    if hasattr(app.state, "postgres_context") and app.state.postgres_context is not None:
        try:
            await app.state.postgres_context.__aexit__(None, None, None)
            logger.info("✅ PostgreSQL checkpointer connection closed")
        except Exception as pg_close_err:
            logger.error(f"Error closing PostgreSQL checkpointer: {pg_close_err}")


# ── FastAPI App ───────────────────────────────────────────────────
app = FastAPI(
    title="RTI-Agent API",
    description="AI-Powered RTI Automation System — Production Grade LangGraph Multi-Agent Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware Stack ──────────────────────────────────────────────
# Order matters: outermost runs first on request, last on response

from api.middleware.tracing_middleware import TracingMiddleware
from api.middleware.request_logging import RequestLoggingMiddleware
from api.middleware.performance_middleware import PerformanceMiddleware

# Starlette add_middleware adds to the TOP of the stack (outermost).
# So we add them in reverse order of desired execution.
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(PerformanceMiddleware)
app.add_middleware(TracingMiddleware)

app.add_middleware(RequestIDMiddleware)           # Inject X-Request-ID
app.add_middleware(RateLimiterMiddleware)         # Rate limiting
app.add_middleware(APIKeyMiddleware)              # Auth

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.APP_ENV == "development" else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "X-API-Key", "Content-Type", "X-Request-ID",
        "X-Trace-ID", "Authorization",
    ],
)

# ── Prometheus metrics endpoint ───────────────────────────────────
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# ── Routers ───────────────────────────────────────────────────────
app.include_router(auth_router)                                        # /auth/*
app.include_router(rti.router, prefix="/api/v1", tags=["RTI"])
app.include_router(status.router, prefix="/api/v1", tags=["Status"])
app.include_router(stream.router, prefix="/api/v1", tags=["Stream"])
app.include_router(health.router, tags=["Health"])
app.include_router(rag.router, prefix="/api/v1")
app.include_router(governance.router, prefix="/api/v1")
app.include_router(tools.router, prefix="/api/v1")
app.include_router(multilingual.router, prefix="/api/v1")
app.include_router(eval.router, prefix="/api/v1")


# ── Global Exception Handler ──────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()

    # Keep response schema consistent with Postman expectations:
    # `detail` must always be an array of error objects.
    # For query_text specifically, adapt the message but preserve array shape.
    for error in errors:
        if "query_text" in error.get("loc", ()):
            adapted = {
                **error,
                "msg": f"Invalid query: {error.get('msg', 'validation failed')}",
            }
            return JSONResponse(status_code=422, content={"detail": [adapted]})

    return JSONResponse(status_code=422, content={"detail": errors})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    from observability.telemetry import telemetry
    telemetry.log_error(exc, operation="http_request")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred.",
            "request_id": getattr(request.state, "request_id", "unknown"),
            "trace_id": getattr(request.state, "trace_id", "unknown"),
        },
    )
