from observability.node_logger import trace_node
"""
graph/nodes/formatter_node.py
------------------------------
FormatterNode — converts sanitized user query into a
legally-structured RTI application draft using Groq 70B.
Invokes translation tool if query is non-English.
"""

import time
import json
from graph.state import RTIAgentState
from llm_router.llm_router import get_llm
from prompts.formatter import build_formatter_prompt
from observability.telemetry import telemetry
from observability.logger import get_logger
from observability.metrics import rti_agent_duration
from multilingual.prompts.multilingual_prompt_router import MultilingualPromptRouter
from multilingual.translation.translator_router import TranslatorRouter

logger = get_logger(__name__)


@trace_node('formatter_node')
async def formatter_node(state: RTIAgentState) -> dict:
    """
    Transforms user query into a formal RTI draft.
    Steps:
    1. Translate to English if needed
    2. Build structured prompt with user context
    3. Call Groq 70B for formal RTI generation
    4. Parse and validate output
    """
    start_time = time.time()
    request_id = state.get("request_id")
    logger.info(f"[FormatterNode] start | request_id={request_id}")

    query = state.get("sanitized_query") or state.get("raw_query", "")
    language = state.get("detected_language") or state.get("language", "en")
    response_language = state.get("response_language") or language or "en"
    user_input = state.get("user_input", {})

    # ── Step 1: Translate if non-English ──────────────────────────
    translated_query = query
    if language != "en":
        try:
            translated = await TranslatorRouter().translate(query, target_language="en", source_language=language)
            translated_query = translated["translated_text"]
            logger.info(f"[FormatterNode] Translated from {language}: {translated_query[:80]}")
        except Exception as e:
            logger.warning(f"[FormatterNode] Translation failed, using original: {e}")

    # ── Step 2: Build prompt ───────────────────────────────────────
    prompt = build_formatter_prompt(
        query=translated_query,
        user_name=user_input.get("name", "Applicant"),
        address=user_input.get("address", ""),
        state_name=user_input.get("state", ""),
        district=user_input.get("district", ""),
    )
    localized_system = MultilingualPromptRouter().get("formatter", response_language)
    if localized_system:
        prompt["system"] = f"{prompt['system']}\n\nLanguage instruction:\n{localized_system}\nReturn the RTI draft in {response_language} unless legal terms are conventionally English."

    # ── Step 3: Call LLM ──────────────────────────────────────────
    llm = get_llm(task="formatting")  # Groq 70B versatile
    formal_query = query  # safe fallback
    rti_template = {}

    try:
        response = await llm.ainvoke([
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": prompt["user"]},
        ])
        raw = response.content.strip()

        # Parse JSON output
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        parsed = json.loads(raw)
        formal_query = parsed.get("formal_query", query)
        rti_template = parsed.get("rti_template", {})

    except json.JSONDecodeError as e:
        logger.warning(f"[FormatterNode] JSON parse failed: {e}. Using raw LLM output.")
        formal_query = raw if raw else query
    except Exception as e:
        logger.error(f"[FormatterNode] LLM call failed: {e}")

    duration_ms = (time.time() - start_time) * 1000
    rti_agent_duration.labels(agent="formatter_node").observe(duration_ms / 1000)

    workflow_path = list(state.get("workflow_path", [])) + ["formatter_node"]

    logger.info(f"[FormatterNode] done | {duration_ms:.0f}ms | formal_query={formal_query[:60]}...")

    return {
        "translated_query": translated_query,
        "formal_query": formal_query,
        "rti_template": rti_template,
        "response_language": response_language,
        "multilingual_context": {
            **state.get("multilingual_context", {}),
            "formatter": {"source_language": language, "response_language": response_language},
        },
        "workflow_path": workflow_path,
        "agent_durations": {**state.get("agent_durations", {}), "formatter_node": duration_ms},
        "llm_models_used": {**state.get("llm_models_used", {}), "formatter_node": "llama-3.3-70b-versatile"},
        "tools_used": [*state.get("tools_used", []), "translate_tool"] if language != "en" else state.get("tools_used", []),
    }
