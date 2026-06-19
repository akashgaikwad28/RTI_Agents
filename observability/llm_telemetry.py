"""
observability/llm_telemetry.py
-------------------------------
Utilities to track LLM costs and usage during execution.
"""

from observability.metrics import rti_estimated_cost_usd, rti_token_usage_total
from observability.telemetry import telemetry
from observability.telemetry_models import Outcome, LogLevel

# Rough estimation pricing (USD per 1k tokens) as placeholders.
# For production, these should be configured dynamically or pulled from a provider API.
COST_TABLE = {
    "groq": {"llama3": {"prompt": 0.0005, "completion": 0.001}},
    "openai": {"gpt-4o": {"prompt": 0.005, "completion": 0.015}},
    "gemini": {"gemini-1.5-pro": {"prompt": 0.0035, "completion": 0.0105}}
}

def estimate_cost(provider: str, model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """Estimates USD cost based on token counts."""
    # Find matching provider (case insensitive substring)
    provider_key = next((p for p in COST_TABLE if p in provider.lower()), None)
    if not provider_key:
        return 0.0
        
    # Find matching model (case insensitive substring)
    model_key = next((m for m in COST_TABLE[provider_key] if m in model_name.lower()), None)
    if not model_key:
        return 0.0
        
    rates = COST_TABLE[provider_key][model_key]
    prompt_cost = (prompt_tokens / 1000) * rates["prompt"]
    completion_cost = (completion_tokens / 1000) * rates["completion"]
    
    return prompt_cost + completion_cost

def track_llm_call(
    operation: str,
    provider: str,
    model_name: str,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: float,
    success: bool = True
):
    """Tracks metrics and logs the LLM call via the central telemetry facade."""
    cost = estimate_cost(provider, model_name, prompt_tokens, completion_tokens)
    
    # Prometheus Metrics
    rti_token_usage_total.labels(model=model_name).inc(prompt_tokens + completion_tokens)
    rti_estimated_cost_usd.labels(model=model_name, provider=provider).inc(cost)
    
    # Structured Log
    telemetry.log_llm_call(
        event="llm_generation_completed" if success else "llm_generation_failed",
        operation=operation,
        provider=provider,
        model_name=model_name,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        estimated_cost_usd=cost,
        latency_ms=latency_ms,
        outcome=Outcome.SUCCESS if success else Outcome.FAILURE,
        level=LogLevel.INFO if success else LogLevel.ERROR
    )
    
    return cost
