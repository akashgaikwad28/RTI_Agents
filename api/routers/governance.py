"""Governance console and AI ecosystem APIs."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from communication.event_bus import get_event_bus
from evaluation.benchmark_runner import evaluate_workflow
from tools.base.tool_registry import get_tool_registry

router = APIRouter(prefix="/governance", tags=["Governance"])


@router.get("/tools")
async def list_tools():
    registry = get_tool_registry()
    return {"tools": [tool.model_dump() for tool in registry.list_tools(permissions=["read:public", "read:rag", "network:gov", "privacy:redact"])]}


@router.post("/tools/{tool_name}/execute")
async def execute_tool(tool_name: str, payload: dict, request: Request):
    registry = get_tool_registry()
    try:
        result = await registry.execute_tool(
            tool_name,
            payload.get("arguments", payload),
            permissions=["read:public", "read:rag", "network:gov", "privacy:redact"],
            request_id=getattr(request.state, "request_id", None),
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return result.model_dump()


@router.get("/events")
async def workflow_events(request_id: str | None = None, limit: int = 100):
    return {"events": [event.model_dump() for event in get_event_bus().history(request_id=request_id, limit=limit)]}


@router.get("/dashboard")
async def governance_dashboard(request: Request):
    mongo = getattr(request.app.state, "mongo", None)
    if mongo is None or getattr(mongo, "db", None) is None:
        return {
            "status": "degraded",
            "reason": "mongo_unavailable",
            "pending_approvals": 0,
            "retrieval_events": 0,
            "tool_logs": len(get_event_bus().history(limit=500)),
            "memory_events": 0,
            "total_audits": 0,
            "compliance_rate": 0.0,
        }
    db = mongo.db
    return {
        "pending_approvals": await db["rti_requests"].count_documents({"approval_status": "pending"}),
        "retrieval_events": await db["retrieval_analytics"].count_documents({}),
        "tool_logs": len(get_event_bus().history(limit=500)),
        "memory_events": await db["adaptive_memory_events"].count_documents({}),
        "total_audits": await db["audit_log"].count_documents({}),
        "compliance_rate": 1.0,
    }


@router.post("/evaluate")
async def evaluate_state(state: dict):
    workflow_state = state.get("state_data", state)
    result = evaluate_workflow(workflow_state)
    result["safety_score"] = max(0.0, min(1.0, 1.0 - float(result.get("hallucination_rate", 0.0))))
    return result
