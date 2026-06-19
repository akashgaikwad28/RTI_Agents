"""LangGraph RetrievalNode backed by the real Phase B hybrid RAG pipeline."""

from __future__ import annotations
from observability.node_logger import trace_node

import time

from config.settings import settings
from graph.state import RTIAgentState
from observability.metrics import rti_agent_duration, rti_retrieval_score
from observability.telemetry import telemetry
from observability.logger import get_logger
from rag.retriever import retrieve_multilingual_results
from rag.retrievers.metadata_filter import infer_department

logger = get_logger(__name__)


@trace_node('retrieval_node')
async def retrieval_node(state: RTIAgentState) -> dict:
    started = time.perf_counter()
    request_id = state.get("request_id")
    formal_query = state.get("formal_query") or state.get("sanitized_query") or state.get("raw_query", "")
    department = infer_department(formal_query, state.get("department", ""))
    language = state.get("detected_language") or state.get("language", "")
    top_k = getattr(settings, "FAISS_TOP_K", settings.RAG_TOP_K)

    logger.info(f"[RetrievalNode] start | request_id={request_id} | department={department}")

    try:
        payload = await retrieve_multilingual_results(
            formal_query,
            department=department,
            k=top_k,
            response_language=state.get("response_language") or language,
        )
        result_rows = payload["results"]
        cache_hit = payload["cache_hit"]
        confidence = payload["confidence"]
    except Exception as exc:
        logger.error(f"[RetrievalNode] retrieval failed | request_id={request_id} | error={exc}", exc_info=True)
        result_rows, cache_hit, confidence, payload = [], False, 0.0, {}

    contexts = [result["text"] for result in result_rows]
    scores = [result["score"] for result in result_rows]
    sources = [result.get("metadata", {}).get("source_url") or result.get("metadata", {}).get("source_path") or result.get("metadata", {}).get("title") for result in result_rows]
    citations = [result["citation"] for result in result_rows]
    metadata = [result["metadata"] for result in result_rows]

    if scores:
        rti_retrieval_score.observe(sum(scores) / len(scores))

    duration_ms = (time.perf_counter() - started) * 1000
    rti_agent_duration.labels(agent="retrieval_node").observe(duration_ms / 1000)

    workflow_path = [*state.get("workflow_path", []), "retrieval_node"]
    logger.info(
        f"[RetrievalNode] done | request_id={request_id} | chunks={len(contexts)} | "
        f"cache_hit={cache_hit} | confidence={confidence:.3f} | latency_ms={duration_ms:.0f}"
    )

    telemetry.log_retrieval(
        event="rag_retrieval",
        operation="retrieval_node",
        query=formal_query,
        latency_ms=duration_ms,
        retrieved_documents=len(contexts),
        final_context_docs=len(contexts),
        cache_hit=cache_hit
    )

    return {
        "department": department or state.get("department", ""),
        "retrieved_context": contexts,
        "retrieval_scores": scores,
        "retrieval_sources": sources,
        "retrieval_citations": citations,
        "retrieval_metadata": metadata,
        "retrieval_confidence": confidence,
        "cache_hit": cache_hit,
        "multilingual_context": {**state.get("multilingual_context", {}), "retrieval": payload},
        "tools_used": [*state.get("tools_used", []), "multilingual_rag_retriever"],
        "workflow_path": workflow_path,
        "agent_durations": {**state.get("agent_durations", {}), "retrieval_node": duration_ms},
    }
