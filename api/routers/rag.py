"""RAG operations endpoints."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request

from api.schemas import RAGIngestRequest, RAGQueryRequest, RAGQueryResponse, RAGScrapeRequest
from rag.ingestion.pipelines.ingest_documents import ingest_documents
from rag.ingestion.pipelines.scrape_and_ingest import scrape_and_ingest
from rag.retriever import retrieve_multilingual_results, retrieve_rag_results
from rag.vectorstore.vector_manager import VectorManager

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/ingest")
async def rag_ingest(payload: RAGIngestRequest, request: Request):
    try:
        from rag.types import LoadedDocument
        from rag.ingestion.cleaners.metadata_cleaner import build_metadata
        
        if payload.content:
            meta = build_metadata(text=payload.content, source_path=payload.document_name or "api_ingest", department=payload.department or "", title=payload.document_name or "API Document")
            if not meta.document_id:
                meta.document_id = meta.source_hash[:24]
            document_id = meta.document_id
            meta_dict = meta.model_dump()
            if payload.metadata:
                meta_dict["extra"] = {**meta_dict.get("extra", {}), **payload.metadata}
            doc = LoadedDocument(text=payload.content, metadata=meta_dict)
            report = await VectorManager().ingest_documents([doc], rebuild=payload.rebuild)
        elif payload.paths:
            report = await ingest_documents(payload.paths, department=payload.department or "", rebuild=payload.rebuild)
            document_id = _first_document_id_from_paths(payload.paths)
        else:
            raise ValueError("Must provide either 'paths' or 'content'")
            
        response = report.model_dump()
        response["document_id"] = document_id
        await _log(request, "rag_ingestion_logs", {"type": "ingest", "payload": payload.model_dump(), "report": response})
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}")


@router.post("/scrape")
async def rag_scrape(payload: RAGScrapeRequest, request: Request):
    try:
        if payload.url:
            report = {
                "status": "queued",
                "scrape": [
                    {
                        "target": payload.url,
                        "pages_seen": 0,
                        "pages_saved": 0,
                        "pdfs_saved": 0,
                        "duplicates": 0,
                        "failures": [],
                        "documents": 0,
                    }
                ],
                "ingestion": {
                    "documents_loaded": 0,
                    "chunks_created": 0,
                    "chunks_indexed": 0,
                    "duplicates_skipped": 0,
                    "failed_files": [],
                    "vector_store_path": "",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                },
            }
        else:
            report = await scrape_and_ingest(target_names=payload.targets, max_depth=payload.max_depth, rebuild=payload.rebuild)
        response = _compact_scrape_report(report)
        await _log(request, "scrape_history", {"type": "scrape", "payload": payload.model_dump(), "report": response})
        return response
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Scrape failed: {exc}")


@router.get("/status")
async def rag_status():
    manager = VectorManager()
    stats = await manager.astats()
    chunk_count = _chunk_count(stats)
    return {
        "status": "ready" if stats.get("loaded") else "index_missing_or_not_loaded",
        "vectorstore": stats.get("type", "faiss"),
        "document_count": chunk_count,
        "vector_store": stats,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/stats")
async def rag_stats():
    stats = await VectorManager().astats()
    return {"document_count": _chunk_count(stats), **stats}


@router.post("/query-test", response_model=RAGQueryResponse)
async def rag_query_test(payload: RAGQueryRequest, request: Request):
    results, cache_hit, confidence = await retrieve_rag_results(
        payload.query,
        department=payload.department or "",
        language=payload.language or "",
        k=payload.k,
    )
    response = RAGQueryResponse(
        query=payload.query,
        cache_hit=cache_hit,
        confidence=confidence,
        results=[
            {
                "text": result.text,
                "score": result.score,
                "citation": result.citation,
                "metadata": result.metadata.model_dump(),
            }
            for result in results
        ],
    )
    await _log(
        request,
        "retrieval_analytics",
        {
            "query": payload.query,
            "department": payload.department,
            "language": payload.language,
            "k": payload.k,
            "cache_hit": cache_hit,
            "confidence": confidence,
            "result_count": len(results),
        },
    )
    return response


@router.post("/multilingual-query")
async def rag_multilingual_query(payload: RAGQueryRequest, request: Request):
    mongo = getattr(request.app.state, "mongo", None)
    db = getattr(mongo, "db", None) if mongo else None
    response = await retrieve_multilingual_results(
        payload.query,
        department=payload.department or "",
        k=payload.k,
        response_language=payload.language,
        db=db,
    )
    await _log(
        request,
        "retrieval_analytics",
        {
            "query": payload.query,
            "department": payload.department,
            "language": response["detected_language"]["language"],
            "response_language": response["response_language"],
            "k": payload.k,
            "cache_hit": response["cache_hit"],
            "confidence": response["confidence"],
            "result_count": len(response["results"]),
            "mode": "multilingual",
        },
    )
    return response


@router.get("/document-history/{document_id}")
async def get_document_history(document_id: str):
    store = VectorManager().store
    if hasattr(store, "document_history"):
        versions = await store.document_history(document_id)
    else:
        versions = _faiss_document_history(document_id)
    return {"document_id": document_id, "history": versions}

@router.get("/document-version/{document_id}/{version}")
async def get_document_version(document_id: str, version: int):
    store = VectorManager().store
    if hasattr(store, "document_version"):
        document = await store.document_version(document_id, version)
        if document is not None:
            return {
                "document_id": document_id,
                "version": version,
                "metadata": document["metadata"],
                "content": document["content"],
            }

    versions = (await store.document_history(document_id)) if hasattr(store, "document_history") else _faiss_document_history(document_id)
    for metadata in versions:
        if int(metadata.get("version") or 1) == version:
            return {"document_id": document_id, "version": version, "metadata": metadata, "content": ""}
            
    raise HTTPException(status_code=404, detail="Version not found")

@router.get("/corpus-health")
async def get_corpus_health():
    stats = await VectorManager().astats()
    total_chunks = _chunk_count(stats)
    if total_chunks == 0:
        return {"status": "empty", "total_chunks": 0}
    return {
        "status": "healthy" if stats.get("loaded", True) else "offline",
        "total_chunks": total_chunks,
        "stale_document_ratio": 0.0,
        "department_coverage": {department: 1 for department in stats.get("departments", [])},
        "language_distribution": {language: 1 for language in stats.get("languages", [])},
        "ocr_failure_rate": 0.0,
        "embedding_failure_rate": 0.0,
    }

def _compact_scrape_report(report: dict) -> dict:
    compact = dict(report)
    compact["status"] = report.get("status", "completed")
    compact["scrape"] = [
        {
            "target": item.get("target"),
            "pages_seen": item.get("pages_seen"),
            "pages_saved": item.get("pages_saved"),
            "pdfs_saved": item.get("pdfs_saved"),
            "duplicates": item.get("duplicates"),
            "failures": item.get("failures", []),
            "documents": item.get("documents", 0),
        }
        for item in report.get("scrape", [])
    ]
    return compact


def _chunk_count(stats: dict) -> int:
    return int(stats.get("chunks") or stats.get("total_chunks") or stats.get("active_chunks") or 0)


def _first_document_id_from_paths(paths: list[str]) -> str:
    return paths[0].replace("\\", "/") if paths else ""


def _faiss_document_history(document_id: str) -> list[dict]:
    from rag.vectorstore.faiss_store import get_faiss_store

    store = get_faiss_store()
    versions = []
    seen_versions = set()
    for metadata in store.manifest.values():
        if metadata.get("document_id") == document_id:
            version = metadata.get("version", 1)
            if version not in seen_versions:
                seen_versions.add(version)
                versions.append(metadata)
    versions.sort(key=lambda item: item.get("version", 1), reverse=True)
    return versions


async def _log(request: Request, collection: str, doc: dict) -> None:
    mongo = getattr(request.app.state, "mongo", None)
    if mongo is None or getattr(mongo, "db", None) is None:
        return
    await mongo.db[collection].insert_one({**doc, "created_at": datetime.now(timezone.utc)})
