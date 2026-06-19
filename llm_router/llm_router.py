"""
llm_router/llm_router.py
-------------------------
Dynamic LLM router with circuit breaker.
Selects the appropriate model based on task type,
provider health, and cost optimization.

Task → Model Mapping:
- routing         → Groq llama-3.1-8b-instant  (fastest, cheapest)
- formatting      → Groq llama-3.3-70b-versatile (smart, fast)
- classification  → Gemini 1.5 Pro (best reasoning)
- review          → Gemini 1.5 Pro (best accuracy)
- reflection      → Groq llama-3.3-70b-versatile (speed + quality)
- fallback        → OpenAI GPT-4o (if all else fails)
"""

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings
from llm_router.circuit_breaker import CircuitBreaker
from observability.structured_logger import get_logger

logger = get_logger(__name__)

# ── Circuit Breakers (one per provider) ───────────────────────────
_groq_breaker = CircuitBreaker(
    name="groq",
    failure_threshold=settings.CIRCUIT_BREAKER_THRESHOLD,
)
_gemini_breaker = CircuitBreaker(
    name="gemini",
    failure_threshold=settings.CIRCUIT_BREAKER_THRESHOLD,
)

# ── Task → Provider Mapping ───────────────────────────────────────
TASK_ROUTING = {
    "routing": ("groq", settings.GROQ_MODEL_FAST),
    "formatting": ("groq", settings.GROQ_MODEL_SMART),
    "classification": ("groq", settings.GROQ_MODEL_SMART),
    "classification_fallback": ("groq", settings.GROQ_MODEL_SMART),
    "review": ("groq", settings.GROQ_MODEL_SMART),
    "reflection": ("groq", settings.GROQ_MODEL_SMART),
    "default": ("groq", settings.GROQ_MODEL_SMART),
}


def _build_groq(model: str, temperature: float = None):
    return ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model=model,
        temperature=temperature or settings.LLM_TEMPERATURE,
    )


def _build_gemini(model: str, temperature: float = None):
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=temperature or settings.LLM_TEMPERATURE,
        convert_system_message_to_human=True,
    )


def get_llm(task: str = "default", temperature: float = None):
    """
    Returns the appropriate LLM instance for a given task.
    Falls back across providers if circuit breaker is open.

    Args:
        task: Task type key (see TASK_ROUTING).
        temperature: Override temperature (uses default if None).

    Returns:
        LangChain chat model instance.
    """
    provider, model = TASK_ROUTING.get(task, TASK_ROUTING["default"])

    # Try primary provider
    if provider == "groq" and not _groq_breaker.is_open:
        try:
            llm = _build_groq(model, temperature)
            logger.debug(f"[LLMRouter] Task={task} → Groq/{model}")
            return llm
        except Exception as e:
            _groq_breaker.record_failure()
            logger.warning(f"[LLMRouter] Groq failed for task={task}: {e}")

    if provider == "gemini" and not _gemini_breaker.is_open:
        try:
            llm = _build_gemini(model, temperature)
            logger.debug(f"[LLMRouter] Task={task} → Gemini/{model}")
            return llm
        except Exception as e:
            _gemini_breaker.record_failure()
            logger.warning(f"[LLMRouter] Gemini failed for task={task}: {e}")

    # Cross-provider fallback
    if provider == "gemini" and not _groq_breaker.is_open:
        logger.warning(f"[LLMRouter] Gemini unavailable → falling back to Groq for task={task}")
        return _build_groq(settings.GROQ_MODEL_SMART, temperature)

    if provider == "groq" and not _gemini_breaker.is_open:
        logger.warning(f"[LLMRouter] Groq unavailable → falling back to Gemini for task={task}")
        return _build_gemini(settings.GEMINI_MODEL, temperature)

    # OpenAI last resort
    if settings.OPENAI_API_KEY:
        logger.warning(f"[LLMRouter] All primary providers down → OpenAI fallback for task={task}")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o",
            temperature=temperature or settings.LLM_TEMPERATURE,
        )

    raise RuntimeError(
        f"[LLMRouter] All LLM providers are unavailable for task={task}. "
        "Check API keys and circuit breaker state."
    )
