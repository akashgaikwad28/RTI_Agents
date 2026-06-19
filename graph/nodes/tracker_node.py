from observability.node_logger import trace_node
"""
graph/nodes/tracker_node.py
----------------------------
TrackerNode — persistence and lifecycle management.
Generates tracking ID, saves full request to MongoDB,
sends submission confirmation, and finalises the state.
"""

import time
import uuid
from datetime import datetime, timezone
from graph.state import RTIAgentState
from mcp_clients.mongo_client import get_mongo_client
from tools.notification_tool import send_submission_notification, send_public_info_notification
from observability.telemetry import telemetry
from observability.logger import get_logger
from observability.metrics import rti_agent_duration

logger = get_logger(__name__)


def _generate_tracking_id() -> str:
    """
    Generate a human-readable RTI tracking ID.
    Format: RTI-YYYYMM-XXXXXX
    """
    now = datetime.now(timezone.utc)
    short_uuid = str(uuid.uuid4()).upper().replace("-", "")[:6]
    return f"RTI-{now.strftime('%Y%m')}-{short_uuid}"


@trace_node('tracker_node')
async def tracker_node(state: RTIAgentState) -> dict:
    """
    Finalises the RTI workflow:
    1. Generates unique tracking ID
    2. Builds complete document for MongoDB
    3. Saves to rti_requests collection
    4. Updates conversation thread
    5. Sends confirmation notification
    6. Returns final response
    """
    start_time = time.time()
    request_id = state.get("request_id")
    intent = state.get("intent", "new_request")
    logger.info(f"[TrackerNode] start | request_id={request_id} | intent={intent}")

    # ── Status Check Path ─────────────────────────────────────────
    if intent == "status_check":
        tracking_id_query = state.get("sanitized_query", "")
        try:
            mongo = await get_mongo_client()
            doc = await mongo.db["rti_requests"].find_one(
                {"tracking_id": {"$regex": tracking_id_query, "$options": "i"}}
            )
            if doc:
                status = doc.get("status", "unknown")
                final_response = (
                    f"Your RTI request (ID: {doc.get('tracking_id')}) "
                    f"is currently: **{status}**.\n"
                    f"Department: {doc.get('department', 'N/A')}\n"
                    f"Submitted: {doc.get('created_at', 'N/A')}"
                )
                return {
                    "tracking_id": doc.get("tracking_id", ""),
                    "final_response": final_response,
                    "status": "status_returned",
                    "workflow_path": [*state.get("workflow_path", []), "tracker_node"],
                }
            else:
                return {
                    "final_response": f"No RTI found matching: {tracking_id_query}",
                    "status": "not_found",
                    "workflow_path": [*state.get("workflow_path", []), "tracker_node"],
                }
        except Exception as e:
            logger.error(f"[TrackerNode] Status check failed: {e}")
            return {"final_response": "Could not retrieve status.", "status": "error", "error": str(e)}

    # ── New Request Path ──────────────────────────────────────────
    if state.get("info_available"):
        tracking_id = _generate_tracking_id()
        public_info = state.get("final_response", "")
        final_response = (
            f"ℹ️ The information you requested is already publicly available!\n\n"
            f"**Information/Link**:\n{public_info}\n\n"
            f"**Tracking ID**: {tracking_id} (Archived for reference)"
        )
        
        rti_doc = {
            "request_id": request_id,
            "tracking_id": tracking_id,
            "thread_id": state.get("thread_id", ""),
            "user_input": state.get("user_input", {}),
            "raw_query": state.get("raw_query", ""),
            "formal_query": state.get("formal_query", ""),
            "rti_template": state.get("rti_template", {}),
            "department": "Public Information Portal",
            "sub_department": "",
            "confidence": "high",
            "retrieved_sources": ["simulated_public_portal"],
            "review_score": 1.0,
            "grounding_score": 1.0,
            "approval_status": "approved",
            "approved_by": "System Intercept",
            "approval_timestamp": datetime.now(timezone.utc).isoformat(),
            "retry_count": 0,
            "workflow_path": state.get("workflow_path", []),
            "tools_used": ["public_portal_lookup"],
            "agent_durations": state.get("agent_durations", {}),
            "llm_models_used": state.get("llm_models_used", {}),
            "status": "completed",
            "info_available": True,
            "final_response": final_response,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        
        try:
            mongo = await get_mongo_client()
            await mongo.db["rti_requests"].update_one(
                {"request_id": request_id},
                {"$set": rti_doc},
                upsert=True
            )
            logger.info(f"[TrackerNode] Saved intercepted public RTI to MongoDB | tracking_id={tracking_id}")

            if state.get("thread_id"):
                await mongo.db["conversation_threads"].update_one(
                    {"thread_id": state["thread_id"]},
                    {
                        "$push": {"requests": tracking_id},
                        "$set": {"active_request_id": tracking_id, "updated_at": datetime.now(timezone.utc)},
                    },
                    upsert=True,
                )
        except Exception as e:
            logger.error(f"[TrackerNode] MongoDB save failed: {e}")

        try:
            await send_public_info_notification(
                email=state.get("user_input", {}).get("email", ""),
                tracking_id=tracking_id,
                query=state.get("raw_query") or state.get("formal_query", ""),
                info=public_info,
            )
        except Exception as e:
            logger.warning(f"[TrackerNode] Public notification failed: {e}")

        duration_ms = (time.time() - start_time) * 1000
        rti_agent_duration.labels(agent="tracker_node").observe(duration_ms / 1000)

        workflow_path = list(state.get("workflow_path", [])) + ["tracker_node"]

        return {
            "tracking_id": tracking_id,
            "final_response": final_response,
            "status": "completed",
            "info_available": True,
            "active_request_id": tracking_id,
            "workflow_path": workflow_path,
            "agent_durations": {**state.get("agent_durations", {}), "tracker_node": duration_ms},
        }

    tracking_id = _generate_tracking_id()
    approval_status = state.get("approval_status", "approved")
    final_status = "submitted" if approval_status == "approved" else "escalated"

    final_response = (
        f"✅ Your RTI application has been successfully submitted!\n\n"
        f"**Tracking ID**: {tracking_id}\n"
        f"**Department**: {state.get('department', 'N/A')}\n"
        f"**Status**: {final_status.title()}\n\n"
        f"You will receive updates at {state.get('user_input', {}).get('email', 'your email')}."
    )

    # Build complete MongoDB document
    rti_doc = {
        "request_id": request_id,
        "tracking_id": tracking_id,
        "thread_id": state.get("thread_id", ""),
        "user_input": state.get("user_input", {}),
        "raw_query": state.get("raw_query", ""),
        "formal_query": state.get("formal_query", ""),
        "rti_template": state.get("rti_template", {}),
        "department": state.get("department", ""),
        "sub_department": state.get("sub_department", ""),
        "confidence": state.get("confidence", ""),
        "retrieved_sources": state.get("retrieval_sources", []),
        "review_score": state.get("review_score", 0.0),
        "grounding_score": state.get("grounding_score", 0.0),
        "approval_status": approval_status,
        "approved_by": state.get("approved_by", ""),
        "approval_timestamp": state.get("approval_timestamp", ""),
        "retry_count": state.get("retry_count", 0),
        "workflow_path": state.get("workflow_path", []),
        "tools_used": state.get("tools_used", []),
        "agent_durations": state.get("agent_durations", {}),
        "llm_models_used": state.get("llm_models_used", {}),
        "status": final_status,
        "final_response": "",  # Save as empty to wait for department's reply
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    try:
        mongo = await get_mongo_client()
        await mongo.db["rti_requests"].update_one(
            {"request_id": request_id},
            {"$set": rti_doc},
            upsert=True
        )
        logger.info(f"[TrackerNode] Saved to MongoDB | tracking_id={tracking_id}")

        # Update conversation thread
        if state.get("thread_id"):
            await mongo.db["conversation_threads"].update_one(
                {"thread_id": state["thread_id"]},
                {
                    "$push": {"requests": tracking_id},
                    "$set": {"active_request_id": tracking_id, "updated_at": datetime.now(timezone.utc)},
                },
                upsert=True,
            )

    except Exception as e:
        logger.error(f"[TrackerNode] MongoDB save failed: {e}")

    # Send confirmation notification
    try:
        await send_submission_notification(
            email=state.get("user_input", {}).get("email", ""),
            tracking_id=tracking_id,
            department=state.get("department", ""),
            formal_query=state.get("formal_query", ""),
        )
    except Exception as e:
        logger.warning(f"[TrackerNode] Notification failed: {e}")

    duration_ms = (time.time() - start_time) * 1000
    rti_agent_duration.labels(agent="tracker_node").observe(duration_ms / 1000)

    workflow_path = list(state.get("workflow_path", [])) + ["tracker_node"]

    logger.info(f"[TrackerNode] done | tracking_id={tracking_id} | {duration_ms:.0f}ms")

    return {
        "tracking_id": tracking_id,
        "final_response": final_response,
        "status": final_status,
        "active_request_id": tracking_id,
        "workflow_path": workflow_path,
        "agent_durations": {**state.get("agent_durations", {}), "tracker_node": duration_ms},
    }
