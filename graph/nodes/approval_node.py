from observability.node_logger import trace_node
"""
graph/nodes/approval_node.py
-----------------------------
ApprovalNode — Human-in-the-loop (HITL) pause point.
The graph is compiled with interrupt_before=["approval_node"].
LangGraph will PAUSE execution here.

The API then:
1. Saves the pending state to MongoDB
2. Notifies user/admin via email
3. Waits for POST /approve/{request_id}
4. Resumes graph with updated approval_status

This node only processes the RESUME path (after human decision).
"""

import time
from datetime import datetime, timezone
from graph.state import RTIAgentState
from tools.notification_tool import send_approval_notification
from mcp_clients.mongo_client import get_mongo_client
from observability.telemetry import telemetry
from observability.logger import get_logger
from observability.metrics import rti_agent_duration, rti_approval_decisions

logger = get_logger(__name__)


@trace_node('approval_node')
async def approval_node(state: RTIAgentState) -> dict:
    """
    HITL Approval node.

    On FIRST entry (before interrupt):
    - Saves pending approval state to MongoDB
    - Sends notification to user/admin

    On RESUME (after human decision via API):
    - Reads approval_status from updated state
    - Applies edited_query if provided
    - Routes accordingly
    """
    start_time = time.time()
    request_id = state.get("request_id")
    approval_status = state.get("approval_status", "pending")

    logger.info(f"[ApprovalNode] request_id={request_id} | status={approval_status}")

    # ── On first entry: save pending state ────────────────────────
    if approval_status == "pending":
        try:
            mongo = await get_mongo_client()
            await mongo.db["rti_requests"].update_one(
                {"request_id": request_id},
                {
                    "$set": {
                        "approval_status": "pending",
                        "formal_query": state.get("formal_query"),
                        "department": state.get("department"),
                        "confidence": state.get("confidence"),
                        "review_score": state.get("review_score"),
                        "status": "awaiting_approval",
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
                upsert=True,
            )

            # Send approval notification
            await send_approval_notification(
                request_id=request_id,
                formal_query=state.get("formal_query", ""),
                department=state.get("department", ""),
                confidence=state.get("confidence", ""),
                review_score=state.get("review_score", 0.0),
                email=state.get("user_input", {}).get("email", ""),
            )

            logger.info(f"[ApprovalNode] Approval pending — graph will interrupt here.")

        except Exception as e:
            logger.error(f"[ApprovalNode] Failed to save pending state: {e}")

        workflow_path = list(state.get("workflow_path", [])) + ["approval_node:pending"]

        return {
            "approval_status": "pending",
            "status": "awaiting_approval",
            "workflow_path": workflow_path,
        }

    # ── On RESUME: process human decision ─────────────────────────
    # Apply human-edited query if provided
    edited_query = state.get("edited_query", "")
    final_query = edited_query if edited_query else state.get("formal_query", "")

    # Emit approval metric
    rti_approval_decisions.labels(decision=approval_status).inc()

    duration_ms = (time.time() - start_time) * 1000
    rti_agent_duration.labels(agent="approval_node").observe(duration_ms / 1000)

    workflow_path = list(state.get("workflow_path", [])) + [f"approval_node:{approval_status}"]

    logger.info(
        f"[ApprovalNode] Resumed | status={approval_status} | "
        f"edited={'yes' if edited_query else 'no'} | {duration_ms:.0f}ms"
    )

    return {
        "formal_query": final_query,  # Use edited version if provided
        "approval_timestamp": datetime.now(timezone.utc).isoformat(),
        "workflow_path": workflow_path,
        "agent_durations": {**state.get("agent_durations", {}), "approval_node": duration_ms},
    }
