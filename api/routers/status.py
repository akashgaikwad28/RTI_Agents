"""
api/routers/status.py
----------------------
RTI status and thread history endpoints.
"""

from fastapi import APIRouter, Request, HTTPException
from api.schemas import RTIStatusResponse, ThreadResponse, FeedbackRequest, FeedbackResponse
from mcp_clients.mongo_client import get_mongo_client
from observability.structured_logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/status/", response_model=RTIStatusResponse)
async def get_rti_status_query(request: Request, tracking_id: str | None = None):
    """Fallback for query param or empty tracking ID."""
    if not tracking_id:
        raise HTTPException(status_code=400, detail="tracking_id is required in path or query")
    return await get_rti_status(tracking_id, request)

@router.get("/status/{tracking_id}", response_model=RTIStatusResponse)
async def get_rti_status(tracking_id: str, request: Request):
    """Retrieve the current status of an RTI by tracking ID."""
    mongo = await get_mongo_client()
    doc = await mongo.get_rti_by_tracking_id(tracking_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"RTI {tracking_id} not found")

    return RTIStatusResponse(
        tracking_id=doc.get("tracking_id", ""),
        status=doc.get("status", ""),
        department=doc.get("department", ""),
        created_at=str(doc.get("created_at", "")),
        updated_at=str(doc.get("updated_at", "")),
        approval_status=doc.get("approval_status"),
        formal_query=doc.get("formal_query"),
        workflow_path=doc.get("workflow_path"),
    )


@router.get("/thread/", response_model=ThreadResponse)
async def get_thread_query(thread_id: str | None = None):
    """Fallback for query param or empty thread ID."""
    if not thread_id:
        raise HTTPException(status_code=400, detail="thread_id is required in path or query")
    return await get_thread(thread_id)

@router.get("/thread/{thread_id}", response_model=ThreadResponse)
async def get_thread(thread_id: str):
    """Retrieve full conversation thread history."""
    mongo = await get_mongo_client()
    doc = await mongo.get_thread(thread_id)
    if not doc:
        return ThreadResponse(
            thread_id=thread_id,
            history=[],
            active_request_id=None,
            created_at="",
            updated_at="",
        )

    return ThreadResponse(
        thread_id=doc.get("thread_id", ""),
        history=doc.get("messages", []),
        active_request_id=doc.get("active_request_id"),
        created_at=str(doc.get("created_at", "")),
        updated_at=str(doc.get("updated_at", "")),
    )


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(payload: FeedbackRequest):
    """Submit user feedback for a completed RTI."""
    mongo = await get_mongo_client()
    await mongo.save_feedback(payload.model_dump())
    logger.info(f"[/feedback] Saved feedback for tracking_id={payload.tracking_id}")
    return FeedbackResponse(status="success", message="Feedback recorded. Thank you!")
