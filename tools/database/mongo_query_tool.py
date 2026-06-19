from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from mcp_clients.mongo_client import get_mongo_client
from tools.base.base_tool import BaseTool


ALLOWED_COLLECTIONS = {
    "rti_requests",
    "conversation_threads",
    "audit_log",
    "retrieval_analytics",
    "rag_ingestion_logs",
    "scrape_history",
    "adaptive_memory_events",
    "feedback",
}


class MongoQueryInput(BaseModel):
    collection: str
    query: dict[str, Any] = Field(default_factory=dict)
    projection: dict[str, Any] | None = None
    limit: int = Field(default=20, ge=1, le=100)


class MongoQueryTool(BaseTool):
    name = "query_mongodb"
    description = "Read-only MongoDB query tool for approved RTI-Agent operational collections."
    category = "database"
    permissions = ["read:rag"]
    capabilities = ["mongodb", "audit", "operational_query"]
    input_schema = MongoQueryInput
    risk_level = "medium"
    timeout_seconds = 10

    async def execute(
        self,
        collection: str,
        query: dict[str, Any] | None = None,
        projection: dict[str, Any] | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        if collection not in ALLOWED_COLLECTIONS:
            raise ValueError(f"Collection is not allowed: {collection}")
        safe_query = query or {}
        _reject_unsafe_query(safe_query)

        mongo = await get_mongo_client()
        cursor = mongo.db[collection].find(safe_query, projection).limit(limit)
        documents = [_json_safe(document) for document in await cursor.to_list(length=limit)]
        return {
            "source": "mongodb",
            "collection": collection,
            "count": len(documents),
            "results": documents,
        }


def _reject_unsafe_query(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {"$where", "$function", "$accumulator"}:
                raise ValueError(f"Unsafe MongoDB operator is not allowed: {key}")
            _reject_unsafe_query(child)
    elif isinstance(value, list):
        for child in value:
            _reject_unsafe_query(child)


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _json_safe(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_json_safe(child) for child in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value) if value.__class__.__name__ == "ObjectId" else value
