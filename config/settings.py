"""
config/settings.py
------------------
Centralized, production-grade configuration using pydantic-settings.
All values are loaded from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal
from functools import lru_cache


class Settings(BaseSettings):

    # ── LLM Providers ─────────────────────────────────────────────
    GROQ_API_KEY: str = Field(..., description="Groq API key (primary LLM)")
    GEMINI_API_KEY: str = Field(..., description="Google Gemini API key")
    OPENAI_API_KEY: str | None = Field(None, description="OpenAI fallback key")

    # ── LLM Model Config ──────────────────────────────────────────
    GROQ_MODEL_FAST: str = Field("llama-3.1-8b-instant", description="Fast Groq model")
    GROQ_MODEL_SMART: str = Field("llama-3.3-70b-versatile", description="Smart Groq model")

    # Primary LLM used by evaluation/"LLM-as-judge" components.
    # Must exist because several detectors reference settings.PRIMARY_MODEL.
    PRIMARY_MODEL: str = Field("llama-3.3-70b-versatile", description="Primary LLM model name for judges")

    GEMINI_MODEL: str = Field("gemini-1.5-pro", description="Gemini reasoning model")
    GEMINI_EMBEDDING_MODEL: str = Field("text-embedding-004", description="Gemini embedding model")
    LLM_TEMPERATURE: float = Field(0.2, description="Default LLM temperature")
    LLM_MAX_RETRIES: int = Field(3, description="LLM call max retries")
    CIRCUIT_BREAKER_THRESHOLD: int = Field(5, description="Failures before circuit opens")

    # ── MongoDB ───────────────────────────────────────────────────
    MONGO_URI: str = Field("mongodb://localhost:27017/", description="MongoDB URI")
    MONGO_DB_NAME: str = Field("rti_db", description="Database name")

    # ── Redis ─────────────────────────────────────────────────────
    REDIS_URL: str = Field("redis://localhost:6379/0", description="Redis connection URL")
    REDIS_SEMANTIC_CACHE_TTL: int = Field(3600, description="Semantic cache TTL in seconds")
    REDIS_SESSION_TTL: int = Field(1800, description="Session TTL in seconds")

    # ── RAG / Vector Store ────────────────────────────────────────
    # Embeddings provider used for both ingestion and runtime retrieval.
    # Keep consistent across ingestion + retrieval to avoid vector dimension mismatches.
    RAG_EMBEDDING_PROVIDER: str = Field(
        "local_sentence_transformers",
        description="Embedding provider: local_sentence_transformers | gemini",
    )
    LOCAL_SENTENCE_TRANSFORMER_MODEL: str = Field(
        "sentence-transformers/all-MiniLM-L6-v2",
        description="Local sentence-transformers model id",
    )

    VECTORSTORE_TYPE: str = Field("faiss", description="Vector store type: faiss | mongodb")
    FAISS_INDEX_PATH: str = Field("data/vector_store", description="FAISS index directory")

    FAISS_TOP_K: int = Field(5, description="Default FAISS top-k retrieval")
    FAISS_ALLOW_DANGEROUS_DESERIALIZATION: bool = Field(False, description="Allow loading trusted local LangChain FAISS docstore pickle")
    RAG_TOP_K: int = Field(5, description="Number of retrieved documents")
    RAG_SIMILARITY_THRESHOLD: float = Field(0.7, description="Minimum similarity score")
    CHUNK_SIZE: int = Field(512, description="Document chunk size")
    CHUNK_OVERLAP: int = Field(80, description="Chunk overlap characters")
    SCRAPE_INTERVAL_HOURS: int = Field(24, description="Default scrape interval for schedulers")
    MAX_SCRAPE_DEPTH: int = Field(1, description="Maximum crawler depth")
    EMBEDDING_BATCH_SIZE: int = Field(32, description="Embedding batch size")
    RAG_CACHE_TTL: int = Field(3600, description="RAG result cache TTL seconds")
    MAX_PDF_SIZE_MB: int = Field(25, description="Maximum PDF download size")

    # ── LangGraph Checkpointer ────────────────────────────────────
    CHECKPOINTER_DB: str = Field("data/checkpoints/rti_checkpoints.db", description="SQLite checkpointer path")
    CHECKPOINTER_TYPE: str = Field("sqlite", description="Checkpointer backend type: sqlite | postgres")
    POSTGRES_CHECKPOINTER_URL: str | None = Field(None, description="Postgres connection URL for checkpointing")

    # ── Security ──────────────────────────────────────────────────
    RTI_API_KEY: str = Field(..., description="API key for endpoint auth — must be set in .env")
    MAX_QUERY_LENGTH: int = Field(2000, description="Max allowed query character length")
    RATE_LIMIT_PER_MINUTE: int = Field(60, description="Requests per minute per API key")
    RATE_LIMIT_PER_IP: int = Field(20, description="Requests per minute per IP")

    # ── JWT Auth ───────────────────────────────────────────────────
    JWT_SECRET_KEY: str = Field(..., description="JWT signing secret — must be set in .env")
    JWT_ALGORITHM: str = Field("HS256", description="JWT signing algorithm")
    JWT_ACCESS_EXPIRE_MINUTES: int = Field(60, description="Access token expiry in minutes")
    JWT_REFRESH_EXPIRE_DAYS: int = Field(7, description="Refresh token expiry in days")

    # ── Admin Seed ────────────────────────────────────────────────
    ADMIN_SEED_EMAIL: str = Field(..., description="Admin seed email — must be set in .env")
    ADMIN_SEED_PASSWORD: str = Field(..., description="Admin seed password — must be set in .env")
    ADMIN_SEED_NAME: str = Field("RTI Admin", description="Admin seed display name")

    # ── Email ─────────────────────────────────────────────────────
    EMAIL_HOST: str = Field("smtp.gmail.com", description="SMTP host")
    EMAIL_PORT: int = Field(587, description="SMTP port")
    EMAIL_USER: str = Field("", description="Sender email address")
    EMAIL_PASSWORD: str | None = Field(None, description="Email password or app token")
    ADMIN_EMAIL: str = Field("admin@rti-system.com", description="Admin email")

    # ── Translation ───────────────────────────────────────────────
    TRANSLATOR_API_ENDPOINT: str = Field("https://libretranslate.de", description="LibreTranslate endpoint")
    TRANSLATOR_API_KEY: str | None = Field(None, description="LibreTranslate API key (optional)")

    # ── Observability & Tracing (LangSmith / Langfuse) ────────────────
    LANGCHAIN_TRACING_V2: bool = Field(False, description="Enable LangSmith tracing")
    LANGCHAIN_ENDPOINT: str = Field("https://api.smith.langchain.com", description="LangSmith endpoint")
    LANGCHAIN_API_KEY: str | None = Field(None, description="LangSmith API key")
    LANGCHAIN_PROJECT: str = Field("rti-agent-prod", description="LangSmith project name")

    LANGFUSE_PUBLIC_KEY: str | None = Field(None, description="Langfuse Public Key")
    LANGFUSE_SECRET_KEY: str | None = Field(None, description="Langfuse Secret Key")
    LANGFUSE_HOST: str = Field("https://cloud.langfuse.com", description="Langfuse Host")

    # ── Evaluation (RAGAS) ────────────────────────────────────────────
    ENABLE_RAGAS_EVALS: bool = Field(False, description="Enable async RAGAS evaluation")

    # ── Security Guardrails ───────────────────────────────────────────
    ENABLE_SECURITY_GUARDRAILS: bool = Field(False, description="Enable LLM-based security guardrails")
    LLAMA_GUARD_MODEL: str = Field("llama-guard-3-8b", description="Model for Llama Guard")

    # ── Logging ───────────────────────────────────────────────────
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_FORMAT: str = Field("json", description="Log format: json | text")

    # ── Agent Workflow ────────────────────────────────────────────
    MAX_REFLECTION_RETRIES: int = Field(2, description="Max self-reflection retry loops")
    HUMAN_APPROVAL_REQUIRED: bool = Field(True, description="Require human approval before submission")
    APPROVAL_TIMEOUT_HOURS: int = Field(24, description="Hours before approval request expires")

    # ── Deployment ────────────────────────────────────────────────
    APP_ENV: Literal["development", "staging", "production"] = Field("development", description="Environment")
    PORT: int = Field(8000, description="API server port")
    WORKERS: int = Field(1, description="Uvicorn worker count")

    # ── OpenTelemetry (Optional) ──────────────────────────────────
    ENABLE_OPENTELEMETRY: bool = Field(False, description="Enable OTEL distributed tracing")
    OTEL_ENDPOINT: str = Field("http://localhost:4317", description="OTEL collector gRPC endpoint")

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    import os
    s = Settings()
    # Explicitly push LangSmith vars to os.environ so LangChain's native tracer works
    if s.LANGCHAIN_TRACING_V2:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        if s.LANGCHAIN_API_KEY:
            os.environ["LANGCHAIN_API_KEY"] = s.LANGCHAIN_API_KEY
        if s.LANGCHAIN_PROJECT:
            os.environ["LANGCHAIN_PROJECT"] = s.LANGCHAIN_PROJECT
        if s.LANGCHAIN_ENDPOINT:
            os.environ["LANGCHAIN_ENDPOINT"] = s.LANGCHAIN_ENDPOINT
    return s


settings = get_settings()
