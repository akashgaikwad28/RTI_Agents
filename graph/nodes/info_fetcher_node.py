from observability.node_logger import trace_node
"""
graph/nodes/info_fetcher_node.py
---------------------------------
InfoFetcherNode — intercepts queries for information that is already
publicly available (matching data/public_rti_knowledge.json).
Bypasses the formal drafting and submission workflow if found.
"""

import time
import os
import json
from graph.state import RTIAgentState
from mcp_clients.mongo_client import get_mongo_client
from observability.logger import get_logger
from observability.metrics import rti_agent_duration

logger = get_logger(__name__)


@trace_node('info_fetcher_node')
async def info_fetcher_node(state: RTIAgentState) -> dict:
    """
    Checks if the query matches known public documents or databases.
    Steps:
    1. Read formal_query or raw_query
    2. Check public_rti_knowledge.json for match
    3. If found, mark state as info_available=True and store in final_response
    4. Otherwise, set info_available=False
    """
    start_time = time.time()
    request_id = state.get("request_id")
    logger.info(f"[InfoFetcherNode] start | request_id={request_id}")

    query = state.get("formal_query") or state.get("sanitized_query") or state.get("raw_query", "")
    info_available = False
    public_info = None

    # ── Step 1: Check simulated public RTI portal (json file) ──────────────────────────
    data_path = os.path.join("data", "public_rti_knowledge.json")
    if os.path.exists(data_path):
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                knowledge_db = json.load(f)
            
            for key, value in knowledge_db.items():
                if key.lower() in query.lower():
                    info_available = True
                    public_info = value
                    logger.info(f"[InfoFetcherNode] Sim Portal Match found for key '{key}': {value}")
                    break
        except Exception as e:
            logger.error(f"[InfoFetcherNode] Failed to load simulated RTI data: {e}")

    # ── Step 2: Fallback/Check MongoDB cache ──────────────────────────
    if not info_available:
        try:
            mongo = await get_mongo_client()
            # Check if there are any completed requests with similar query that contain the response
            doc = await mongo.db["rti_requests"].find_one({
                "status": "completed",
                "info_available": True,
                "raw_query": {"$regex": query, "$options": "i"}
            })
            if doc:
                info_available = True
                public_info = doc.get("final_response")
                logger.info(f"[InfoFetcherNode] MongoDB Cache Match found: {public_info}")
        except Exception as e:
            logger.debug(f"[InfoFetcherNode] MongoDB lookup skipped or failed: {e}")

    duration_ms = (time.time() - start_time) * 1000
    rti_agent_duration.labels(agent="info_fetcher_node").observe(duration_ms / 1000)

    workflow_path = list(state.get("workflow_path", [])) + ["info_fetcher_node"]

    if info_available:
        logger.info(f"[InfoFetcherNode] done | Intercepted query successfully | {duration_ms:.0f}ms")
        return {
            "info_available": True,
            "final_response": public_info,
            "status": "completed",
            "workflow_path": workflow_path,
            "agent_durations": {**state.get("agent_durations", {}), "info_fetcher_node": duration_ms},
            "llm_models_used": {**state.get("llm_models_used", {}), "info_fetcher_node": "rule-engine"},
        }
    else:
        logger.info(f"[InfoFetcherNode] done | Query not in public records | {duration_ms:.0f}ms")
        return {
            "info_available": False,
            "workflow_path": workflow_path,
            "agent_durations": {**state.get("agent_durations", {}), "info_fetcher_node": duration_ms},
        }
