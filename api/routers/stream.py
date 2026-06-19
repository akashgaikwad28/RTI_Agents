"""
api/routers/stream.py
----------------------
SSE (Server-Sent Events) streaming endpoint.
Streams real-time LangGraph execution progress to the client.

Usage:
  GET /api/v1/stream/{request_id}
  Accept: text/event-stream

Events emitted:
  {"agent": "formatter_node", "status": "running"}
  {"agent": "formatter_node", "status": "done", "duration_ms": 1240}
  {"event": "complete", "tracking_id": "RTI-202405-ABCDEF"}
  {"event": "error", "message": "..."}
"""

import json
import asyncio
from fastapi import APIRouter, Request, HTTPException
from sse_starlette.sse import EventSourceResponse
from observability.structured_logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/stream/{request_id}")
async def stream_workflow(request_id: str, http_request: Request):
    """
    Stream real-time LangGraph node execution events via SSE.
    The client connects here after POST /submit and sees live progress.
    """
    logger.info(f"[/stream] SSE connection | request_id={request_id}")
    graph = http_request.app.state.graph
    config = {"configurable": {"thread_id": request_id}}

    async def event_generator():
        try:
            previous_nodes = set()
            while True:
                state = await graph.aget_state(config)
                if not state:
                    await asyncio.sleep(1)
                    continue

                workflow_path = state.values.get("workflow_path", [])
                
                # Stream newly completed nodes
                for node in workflow_path:
                    if node not in previous_nodes:
                        yield {"event": "agent_start", "data": json.dumps({"agent": node, "status": "running"})}
                        yield {"event": "agent_done", "data": json.dumps({"agent": node, "status": "done", "duration_ms": round(state.values.get("agent_durations", {}).get(node, 0))})}
                        previous_nodes.add(node)

                next_nodes = state.next
                if next_nodes and "approval_node" in next_nodes:
                    yield {
                        "event": "approval_required",
                        "data": json.dumps({
                            "message": "RTI draft ready for human review",
                            "request_id": request_id,
                            "approve_url": f"/api/v1/approve/{request_id}",
                        }),
                    }
                    break
                
                if not next_nodes and "tracker_node" in workflow_path:
                    yield {
                        "event": "complete",
                        "data": json.dumps({
                            "tracking_id": state.values.get("tracking_id", ""),
                            "status": state.values.get("status", "completed"),
                            "message": state.values.get("final_response", ""),
                        }),
                    }
                    break

                if await http_request.is_disconnected():
                    logger.info(f"[/stream] Client disconnected | request_id={request_id}")
                    break

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info(f"[/stream] Stream cancelled | request_id={request_id}")
        except Exception as e:
            logger.error(f"[/stream] Stream error: {e}")
            yield {
                "event": "error",
                "data": json.dumps({"message": str(e)}),
            }

    return EventSourceResponse(event_generator())
