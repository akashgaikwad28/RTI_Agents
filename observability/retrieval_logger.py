"""
observability/retrieval_logger.py
----------------------------------
Domain logger for RAG retrieval operations. Tracks provenance.
"""

from typing import List, Dict, Any
from observability.telemetry import telemetry
from observability.telemetry_models import Outcome

def log_provenance(
    query: str,
    latency_ms: float,
    retrieved_docs: List[Dict[str, Any]],
    reranked_docs: List[Dict[str, Any]],
    final_docs: List[Dict[str, Any]],
    dropped_docs: List[Dict[str, Any]],
    cache_hit: bool = False
):
    """
    Logs full RAG provenance for debugging hallucinations.
    Only writes the metadata IDs/scores, not full text, to avoid massive logs.
    """
    # Extract IDs/sources for logging instead of full text payload
    def _extract_meta(docs):
        return [{"id": d.get("id"), "score": d.get("score")} for d in docs]
        
    telemetry.log_retrieval(
        event="rag_retrieval_completed",
        operation="vector_search",
        query=query,
        latency_ms=latency_ms,
        retrieved_documents=len(retrieved_docs),
        reranked_documents=len(reranked_docs),
        final_context_docs=len(final_docs),
        dropped_documents=len(dropped_docs),
        cache_hit=cache_hit,
        outcome=Outcome.SUCCESS
    )
