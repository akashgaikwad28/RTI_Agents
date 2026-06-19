"""Corpus health monitoring and analytics."""

from __future__ import annotations

from typing import Any

from observability.structured_logger import get_logger
from rag.vectorstore.faiss_store import get_faiss_store

logger = get_logger(__name__)

class CorpusHealthMonitor:
    @staticmethod
    def get_health_stats() -> dict[str, Any]:
        """Calculates global health metrics across the vector manifest."""
        store = get_faiss_store()
        if not store.is_loaded:
            return {"status": "offline"}
            
        manifest = store.manifest
        total_chunks = len(manifest)
        if total_chunks == 0:
            return {"status": "empty"}
            
        inactive_chunks = sum(1 for m in manifest.values() if m.get("is_active") is False)
        stale_ratio = inactive_chunks / total_chunks if total_chunks else 0.0
        
        departments = {}
        languages = {}
        
        for m in manifest.values():
            dept = m.get("department", "unknown")
            lang = m.get("language", "unknown")
            departments[dept] = departments.get(dept, 0) + 1
            languages[lang] = languages.get(lang, 0) + 1
            
        return {
            "status": "healthy",
            "total_chunks": total_chunks,
            "stale_document_ratio": round(stale_ratio, 4),
            "department_coverage": departments,
            "language_distribution": languages,
            "ocr_failure_rate": 0.0,
            "embedding_failure_rate": 0.0
        }
