"""Enterprise MCP-style tool APIs for frontend visualization and replay."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Request

from tools.base.tool_registry import get_tool_registry
from tools.base.tool_schemas import ToolCallPlan, ToolQueryRequest, ToolQueryResponse
from tools.debate.debate_manager import DebateManager
from tools.evaluation.tool_benchmark import benchmark_results
from tools.execution.async_executor import AsyncToolExecutor
from tools.memory.tool_memory import ToolMemory
from tools.planning.planning_agent import PlanningAgent

router = APIRouter(prefix="/tools", tags=["Tools"])


@router.get("")
async def list_tools(permissions: str | None = None, capability: str | None = None, department: str | None = None):
    registry = get_tool_registry()
    granted = permissions.split(",") if permissions else ["read:public", "read:rag", "network:gov", "privacy:redact"]
    if capability:
        tools = registry.get_tools_by_capability(capability, permissions=granted)
    elif department:
        tools = registry.get_tools_by_department(department, permissions=granted)
    else:
        tools = registry.list_tools(permissions=granted)
    return {"tools": [tool.model_dump() for tool in tools]}


@router.get("/status")
async def tool_status():
    registry = get_tool_registry()
    statuses = []
    for metadata in registry.list_tools(permissions=["read:public", "read:rag", "network:gov", "privacy:redact"]):
        tool = registry.get_tool(metadata.name)
        statuses.append({"tool": metadata.model_dump(), "health": await tool.health_check()})
    return {"status": "ok", "tools": statuses}


@router.post("/query", response_model=ToolQueryResponse)
async def query_tools(payload: ToolQueryRequest, request: Request):
    request_id = getattr(request.state, "request_id", None) or str(uuid.uuid4())
    planning = await PlanningAgent().plan(
        payload.query,
        department=payload.department or "",
        language=payload.language,
        permissions=payload.permissions,
        max_tools=payload.max_tools,
    )
    calls = [ToolCallPlan.model_validate(call) for call in planning["execution_plan"]["tool_calls"]]
    results = await AsyncToolExecutor().run_plan(
        calls,
        permissions=payload.permissions,
        request_id=request_id,
        department=payload.department,
    )
    serialized = [result.model_dump() for result in results]
    debate = DebateManager().run(serialized)
    validation = {
        "valid_results": sum(1 for r in serialized if r.get("validation", {}).get("valid") or r.get("status") == "success"),
        "total_results": len(serialized),
        "benchmark": benchmark_results(serialized),
    }
    consensus = debate["consensus"]
    mongo = getattr(request.app.state, "mongo", None)
    db = getattr(mongo, "db", None) if mongo else None
    await ToolMemory().record_workflow(db, request_id, planning["execution_plan"], serialized, consensus)
    return ToolQueryResponse(
        execution_plan=planning["execution_plan"],
        selected_tools=planning["selected_tools"],
        tool_results=results,
        debate=debate,
        validation=validation,
        consensus=consensus,
        reasoning_trace=planning["reasoning_trace"] + [{"agent": "tool_query_api", "parallel_tool_calls": len(calls)}],
    )


@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    return {"trace_id": trace_id, "events": get_tool_registry().executor.traces(trace_id)}


@router.get("/metrics")
async def get_tool_metrics():
    traces = get_tool_registry().executor.traces()
    results = [event["result"] for event in traces]
    return {"window_size": len(results), "benchmark": benchmark_results(results)}


@router.post("/benchmark")
async def benchmark(payload: ToolQueryRequest, request: Request):
    if payload.queries:
        results = []
        for query in payload.queries:
            single = payload.model_copy(update={"query": query, "queries": None})
            response = await query_tools(single, request)
            results.append({"query": query, "benchmark": response.validation["benchmark"], "consensus": response.consensus})
        return {"queries": payload.queries, "iterations": payload.iterations, "results": results, "benchmark": benchmark_results([item["benchmark"] for item in results])}
    response = await query_tools(payload, request)
    return {"query": payload.query, "benchmark": response.validation["benchmark"], "consensus": response.consensus}


@router.post("/replay")
async def replay(payload: dict, request: Request):
    calls = [ToolCallPlan.model_validate(call) for call in payload.get("tool_calls", [])]
    permissions = payload.get("permissions") or ["read:public", "read:rag", "network:gov", "privacy:redact"]
    results = await AsyncToolExecutor().run_plan(
        calls,
        permissions=permissions,
        request_id=payload.get("request_id") or getattr(request.state, "request_id", None),
        department=payload.get("department"),
    )
    serialized = [result.model_dump() for result in results]
    return {"results": serialized, "debate": DebateManager().run(serialized), "benchmark": benchmark_results(serialized)}
