"""
api/routers/rti.py
-------------------
Core RTI workflow endpoints.
POST /submit  — Start new RTI workflow
POST /approve — Human approval/rejection of pending RTI
"""

import re
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Request, HTTPException, Depends
from api.schemas import RTISubmitRequest, RTISubmitResponse, ApprovalRequest, ApprovalResponse, RespondRequest, RespondResponse
from graph.state import RTIAgentState
from mcp_clients.mongo_client import get_mongo_client
from security.sanitizer import sanitize_query
from security.pii_masker import mask_pii
from observability.structured_logger import get_logger
from observability.metrics import rti_requests_total, rti_active_requests
from observability.audit_logger import log_audit_action
from api.auth.jwt_handler import get_current_user
from tools.department_lookup import get_canonical_departments_for_registration

logger = get_logger(__name__)
router = APIRouter()


@router.post("/submit", response_model=RTISubmitResponse, status_code=202)
async def submit_rti(payload: RTISubmitRequest, request: Request):
    """
    Submit a new RTI request.
    Starts the LangGraph workflow asynchronously.

    Returns:
        request_id: Use this to stream progress and poll status.
    """
    request_id = str(uuid.uuid4())
    thread_id = payload.thread_id or str(uuid.uuid4())

    logger.info(f"[/submit] request_id={request_id} | query={payload.query_text[:60]}")

    # ── Sanitize input ─────────────────────────────────────────────
    try:
        sanitized_query = sanitize_query(payload.query_text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=f"Invalid query: {str(e)}")

    # ── Build initial state ────────────────────────────────────────
    initial_state: RTIAgentState = {
        "request_id": request_id,
        "thread_id": thread_id,
        "session_id": getattr(request.state, "request_id", request_id),
        "user_input": payload.model_dump(),
        "raw_query": payload.query_text,
        "language": payload.language or "en",
        "uploaded_documents": [],
        "conversation_history": [],
        "active_request_id": "",
        "translated_query": "",
        "sanitized_query": sanitized_query,
        "formal_query": "",
        "rti_template": {},
        "department": "",
        "sub_department": "",
        "confidence": "",
        "classification_notes": "",
        "retrieved_context": [],
        "retrieval_scores": [],
        "retrieval_sources": [],
        "retrieval_citations": [],
        "retrieval_metadata": [],
        "retrieval_confidence": 0.0,
        "tools_used": [],
        "cache_hit": False,
        "review_passed": False,
        "review_feedback": "",
        "review_score": 0.0,
        "grounding_score": 0.0,
        "hallucination_flags": [],
        "reflection_needed": False,
        "reflection_reason": "",
        "retry_count": 0,
        "max_retries": 2,
        "approval_required": True,
        "approval_status": "pending",
        "approved_by": "",
        "approval_timestamp": "",
        "edited_query": "",
        "tracking_id": "",
        "final_response": "",
        "status": "pending",
        "error": None,
        "next_agent": "router_node",
        "intent": "new_request",
        "workflow_path": [],
        "agent_durations": {},
        "token_counts": {},
        "llm_models_used": {},
        "execution_plan": {},
        "selected_tools": [],
        "tool_results": [],
        "agent_debate": {},
        "critic_feedback": {},
        "verification_report": {},
        "consensus_result": {},
        "final_ai_decision": {},
        "ai_risk_score": 0.0,
        "escalation_required": False,
        "learning_feedback": {},
        "reasoning_trace": [],
        "live_events": [],
        "governance_notes": [],
    }

    # ── Run graph asynchronously ───────────────────────────────────
    graph = request.app.state.graph
    config = {"configurable": {"thread_id": request_id}}

    mongo = getattr(request.app.state, "mongo", None) or await get_mongo_client()
    now = datetime.now(timezone.utc)
    await mongo.db["conversation_threads"].update_one(
        {"thread_id": thread_id},
        {
            "$setOnInsert": {
                "thread_id": thread_id,
                "messages": [],
                "requests": [],
                "created_at": now,
            },
            "$set": {
                "active_request_id": request_id,
                "updated_at": now,
            },
        },
        upsert=True,
    )

    # Save an initial draft of the RTI so frontend polling doesn't 404 while graph processes
    initial_rti_doc = {
        "request_id": request_id,
        "thread_id": thread_id,
        "tracking_id": f"RTI-PENDING-{request_id[:6]}",
        "raw_query": payload.query_text,
        "user_input": payload.model_dump(),
        "department": "Analyzing...",
        "status": "processing",
        "approval_status": "pending",
        "created_at": now,
        "updated_at": now,
    }
    await mongo.insert_rti_request(initial_rti_doc)

    rti_active_requests.inc()
    rti_requests_total.labels(intent="new_request").inc()

    log_audit_action(
        actor="system",
        action="rti_submitted",
        reason="New RTI request submitted by user",
        after_state={"request_id": request_id, "query": payload.query_text}
    )

    async def run_workflow():
        try:
            await graph.ainvoke(initial_state, config=config)
            logger.info(f"[/submit] Graph paused at approval | request_id={request_id}")

            # Persist enriched state to MongoDB after graph pauses
            try:
                graph_state = await graph.aget_state(config)
                if graph_state and graph_state.values:
                    enriched = graph_state.values
                    enriched_update = {
                        "formal_query": enriched.get("formal_query", ""),
                        "department": enriched.get("department", ""),
                        "sub_department": enriched.get("sub_department", ""),
                        "confidence": enriched.get("confidence", ""),
                        "retrieval_confidence": enriched.get("retrieval_confidence", 0.0),
                        "retrieval_citations": enriched.get("retrieval_citations", []),
                        "retrieval_sources": enriched.get("retrieval_sources", []),
                        "review_score": enriched.get("review_score", 0.0),
                        "grounding_score": enriched.get("grounding_score", 0.0),
                        "hallucination_flags": enriched.get("hallucination_flags", []),
                        "workflow_path": enriched.get("workflow_path", []),
                        "agent_durations": enriched.get("agent_durations", {}),
                        "reasoning_trace": enriched.get("reasoning_trace", []),
                        "ai_risk_score": enriched.get("ai_risk_score", 0.0),
                        "tools_used": enriched.get("tools_used", []),
                        "status": "awaiting_approval",
                        "approval_status": "pending",
                        "updated_at": datetime.now(timezone.utc),
                    }
                    _mongo = getattr(request.app.state, "mongo", None) or await get_mongo_client()
                    await _mongo.db["rti_requests"].update_one(
                        {"request_id": request_id},
                        {"$set": enriched_update},
                    )
                    logger.info(f"[/submit] Enriched state persisted | request_id={request_id} | dept={enriched.get('department')}")
            except Exception as persist_err:
                logger.error(f"[/submit] Failed to persist enriched state: {persist_err}")

        except Exception as e:
            logger.error(f"[/submit] Graph execution failed: {e}")
            try:
                _mongo = getattr(request.app.state, "mongo", None) or await get_mongo_client()
                await _mongo.db["rti_requests"].update_one(
                    {"request_id": request_id},
                    {"$set": {"status": "error", "error": str(e), "updated_at": datetime.now(timezone.utc)}},
                )
            except Exception:
                pass
        finally:
            rti_active_requests.dec()

    request.app.state.background_tasks = getattr(request.app.state, "background_tasks", set())
    import asyncio
    task = asyncio.create_task(run_workflow())
    request.app.state.background_tasks.add(task)
    task.add_done_callback(request.app.state.background_tasks.discard)

    return RTISubmitResponse(
        request_id=request_id,
        thread_id=thread_id,
        status="awaiting_approval",
        message="Your RTI is being processed. You will be notified for approval.",
        stream_url=f"/api/v1/stream/{request_id}",
    )


@router.post("/approve/{request_id}", response_model=ApprovalResponse)
async def approve_rti(
    request_id: str,
    payload: ApprovalRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Human approval/rejection of a pending RTI draft.
    Resumes the LangGraph from the approval_node interrupt.

    Body:
        decision: "approved" | "rejected"
        approved_by: Name/ID of approver
        edited_query: Optional human-edited query
    """
    logger.info(f"[/approve] request_id={request_id} | decision={payload.decision} | user={current_user.get('email')}")

    if payload.decision not in ("approved", "rejected"):
        raise HTTPException(status_code=422, detail="decision must be 'approved' or 'rejected'")

    mongo = getattr(request.app.state, "mongo", None) or await get_mongo_client()
    existing = await mongo.get_rti_by_request_id(request_id)
    if not existing:
        raise HTTPException(status_code=404, detail="RTI request not found")

    # Enforce request ownership for citizen role
    role = current_user.get("role")
    email = current_user.get("email")
    if role == "citizen" and email:
        user_input = existing.get("user_input") or {}
        doc_email = user_input.get("email") or existing.get("email")
        if doc_email != email:
            raise HTTPException(status_code=403, detail="You do not have permission to approve this request")

    # ── Resume LangGraph with approval state update ────────────────
    graph = request.app.state.graph
    config = {"configurable": {"thread_id": request_id}}
    if existing and existing.get("tracking_id") and not existing.get("tracking_id", "").startswith("RTI-PENDING-"):
        await mongo.update_rti_status(
            request_id,
            existing.get("status", "completed"),
            {
                "approval_status": payload.decision,
                "approved_by": payload.approved_by or "system",
                "approval_timestamp": datetime.now(timezone.utc).isoformat(),
                "edited_query": payload.edited_query or "",
            },
        )
        return ApprovalResponse(
            request_id=request_id,
            tracking_id=existing.get("tracking_id", ""),
            status=existing.get("status", "completed"),
            message=existing.get("final_response", "RTI workflow approval recorded."),
        )

    import asyncio
    max_wait = 60
    waited = 0
    while waited < max_wait:
        state = await graph.aget_state(config)
        if state and state.next and "approval_node" in state.next:
            break
        await asyncio.sleep(1)
        waited += 1

    if waited >= max_wait:
        raise HTTPException(status_code=504, detail="Timeout waiting for graph to reach approval_node.")

    resume_state = {
        "approval_status": payload.decision,
        "approved_by": payload.approved_by or "system",
        "approval_timestamp": datetime.now(timezone.utc).isoformat(),
        "edited_query": payload.edited_query or "",
    }

    log_audit_action(
        actor=current_user.get("email") or payload.approved_by or "system",
        action=f"rti_{payload.decision}",
        reason=f"Human review decision: {payload.decision}",
        before_state={"status": "awaiting_approval"},
        after_state=resume_state,
        department=existing.get("department", "unknown")
    )

    try:
        await graph.aupdate_state(config, resume_state)
        result = await graph.ainvoke(None, config=config)
        tracking_id = result.get("tracking_id", "")
        if not tracking_id:
            persisted = await mongo.get_rti_by_request_id(request_id)
            tracking_id = (persisted or {}).get("tracking_id", "")
        final_status = result.get("status", "unknown")

        return ApprovalResponse(
            request_id=request_id,
            tracking_id=tracking_id,
            status=final_status,
            message=result.get("final_response", "RTI workflow completed."),
        )

    except Exception as e:
        logger.error(f"[/approve] Resume failed: {e}")
        raise HTTPException(status_code=500, detail=f"Approval processing failed: {str(e)}")


def _map_rti_to_frontend(doc: dict) -> dict:
    created_at = doc.get("created_at")
    updated_at = doc.get("updated_at")
    
    return {
        "id": doc.get("request_id") or str(doc.get("_id", "")),
        "requestId": doc.get("request_id", ""),
        "trackingId": doc.get("tracking_id", ""),
        "title": doc.get("raw_query", "")[:50] + "...",
        "queryText": doc.get("raw_query", ""),
        "formalQuery": doc.get("formal_query"),
        "department": doc.get("department", ""),
        "status": doc.get("status", "pending"),
        "approvalStatus": doc.get("approval_status", "pending"),
        "confidence": str(doc.get("retrieval_confidence", "")),
        "retrievalConfidence": doc.get("retrieval_confidence"),
        "aiRiskScore": doc.get("ai_risk_score"),
        "createdAt": created_at.isoformat() if hasattr(created_at, "isoformat") else str(created_at),
        "updatedAt": updated_at.isoformat() if hasattr(updated_at, "isoformat") else str(updated_at),
        "citations": doc.get("retrieval_citations", []),
        "reasoningTrace": doc.get("reasoning_trace", []),
        "workflowPath": doc.get("workflow_path", []),
        "agentDurations": doc.get("agent_durations", {}),
        "hallucinationFlags": doc.get("hallucination_flags", []),
        "finalResponse": doc.get("final_response"),
        "officerResponse": doc.get("officer_response"),
        "respondedBy": doc.get("responded_by"),
        "respondedAt": doc.get("responded_at"),
        "userInput": doc.get("user_input", {}),
    }

@router.get("/rtis", response_model=dict)
@router.get("/rtis/", response_model=dict, include_in_schema=False)
async def list_rtis(
    request: Request,
    page: int = 1,
    limit: int = 10,
    status: str | None = None,
    department: str | None = None,
    current_user: dict = Depends(get_current_user),
):
    """
    List RTIs with pagination and optional filters.
    If the logged-in user is a citizen, only show their own requests.
    If the logged-in user is an officer, show requests for their department.
    If they are an admin, show all requests.
    """
    mongo = getattr(request.app.state, "mongo", None) or await get_mongo_client()
    query = {}
    if status:
        query["status"] = status
    if department:
        query["department"] = department
        
    role = current_user.get("role")
    email = current_user.get("email")
    
    if role == "citizen" and email:
        query["$or"] = [
            {"user_input.email": email},
            {"email": email}
        ]
    elif role == "officer":
        user_id = current_user.get("sub")
        db_user = await mongo.get_user_by_id(user_id) if user_id else None
        if db_user and db_user.get("department"):
            canon_depts = get_canonical_departments_for_registration(db_user.get("department"))
            if canon_depts:
                regex_pattern = "^(" + "|".join([re.escape(d) for d in canon_depts]) + ")$"
                query["department"] = {"$regex": regex_pattern, "$options": "i"}
            
    rtis = await mongo.list_rtis(page=page, limit=limit, filter_query=query)
    total = await mongo.count_rtis(filter_query=query)
    
    mapped_rtis = [_map_rti_to_frontend(doc) for doc in rtis]
        
    return {
        "data": mapped_rtis,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": max(1, (total + limit - 1) // limit)
    }


@router.get("/rtis/assigned", response_model=dict)
async def list_assigned_rtis(
    request: Request,
    page: int = 1,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
):
    """
    List RTIs assigned to the currently logged in officer based on their department.
    """
    mongo = getattr(request.app.state, "mongo", None) or await get_mongo_client()
    
    if current_user.get("role") not in ("officer", "admin"):
        raise HTTPException(status_code=403, detail="Only officers or admins can access assigned queue")
        
    user_id = current_user.get("sub")
    db_user = await mongo.get_user_by_id(user_id) if user_id else None
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    dept = db_user.get("department")
    if not dept and current_user.get("role") != "admin":
        raise HTTPException(status_code=400, detail="Officer has no assigned department")
        
    query = {}
    if current_user.get("role") != "admin" and dept:
        canon_depts = get_canonical_departments_for_registration(dept)
        if canon_depts:
            regex_pattern = "^(" + "|".join([re.escape(d) for d in canon_depts]) + ")$"
            query["department"] = {"$regex": regex_pattern, "$options": "i"}
        
    rtis = await mongo.list_rtis(page=page, limit=limit, filter_query=query)
    total = await mongo.count_rtis(filter_query=query)
    
    mapped_rtis = [_map_rti_to_frontend(doc) for doc in rtis]
    
    return {
        "data": mapped_rtis,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": max(1, (total + limit - 1) // limit)
    }


@router.get("/rtis/{request_id}", response_model=dict)
async def get_rti(
    request_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Get details of a specific RTI request.
    If the logged-in user is a citizen, ensure the request belongs to them.
    If the logged-in user is an officer, ensure the request belongs to their department.
    """
    mongo = getattr(request.app.state, "mongo", None) or await get_mongo_client()
    doc = await mongo.get_rti_by_request_id(request_id)
    if not doc:
        raise HTTPException(status_code=404, detail="RTI not found")
        
    role = current_user.get("role")
    email = current_user.get("email")
    
    if role == "citizen" and email:
        user_input = doc.get("user_input") or {}
        doc_email = user_input.get("email") or doc.get("email")
        if doc_email != email:
            raise HTTPException(status_code=403, detail="You do not have permission to view this RTI request")
            
    elif role == "officer":
        user_id = current_user.get("sub")
        db_user = await mongo.get_user_by_id(user_id) if user_id else None
        if db_user:
            dept = db_user.get("department")
            doc_dept = doc.get("department")
            if dept and doc_dept:
                canon_depts = get_canonical_departments_for_registration(dept)
                if not any(d.strip().lower() == doc_dept.strip().lower() for d in canon_depts):
                    raise HTTPException(status_code=403, detail="You do not have permission to view requests of this department")
                
    return _map_rti_to_frontend(doc)


@router.post("/rtis/{request_id}/respond", response_model=RespondResponse)
async def respond_to_rti(
    request_id: str,
    payload: RespondRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    """
    Allows a department officer (or admin) to respond to an RTI request.
    This updates the status to 'completed', registers their response, and sends an email to the citizen.
    """
    logger.info(f"[/rtis/{request_id}/respond] user={current_user.get('email')} | role={current_user.get('role')}")

    if current_user.get("role") not in ("officer", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Only department officers or administrators can respond to RTI requests."
        )

    mongo = getattr(request.app.state, "mongo", None) or await get_mongo_client()
    doc = await mongo.get_rti_by_request_id(request_id)
    if not doc:
        raise HTTPException(status_code=404, detail="RTI request not found")

    # Enforce department ownership for officers
    if current_user.get("role") == "officer":
        user_id = current_user.get("sub")
        db_user = await mongo.get_user_by_id(user_id) if user_id else None
        if not db_user:
            raise HTTPException(status_code=404, detail="Officer user account not found.")

        dept = db_user.get("department")
        doc_dept = doc.get("department")
        if not dept:
            raise HTTPException(status_code=400, detail="Officer has no assigned department.")

        if doc_dept:
            canon_depts = get_canonical_departments_for_registration(dept)
            if not any(d.strip().lower() == doc_dept.strip().lower() for d in canon_depts):
                raise HTTPException(
                    status_code=403,
                    detail="You do not have permission to respond to requests of this department."
                )

    # Perform updates in MongoDB
    tracking_id = doc.get("tracking_id") or ""
    now = datetime.now(timezone.utc)
    
    update_data = {
        "status": "completed",
        "final_response": payload.response_text,
        "officer_response": payload.response_text,
        "responded_by": current_user.get("email"),
        "responded_at": now.isoformat(),
        "updated_at": now,
    }

    await mongo.db["rti_requests"].update_one(
        {"request_id": request_id},
        {"$set": update_data}
    )

    # Dispatch email notification asynchronously
    citizen_email = doc.get("user_input", {}).get("email") or doc.get("email")
    if citizen_email:
        try:
            from tools.notification_tool import send_officer_response_notification
            responded_at_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
            await send_officer_response_notification(
                email=citizen_email,
                tracking_id=tracking_id,
                department=doc.get("department", "Government Department"),
                query=doc.get("raw_query") or doc.get("formal_query") or "RTI Request",
                response_text=payload.response_text,
                responded_at=responded_at_str,
            )
        except Exception as email_err:
            logger.warning(f"[/rtis/{request_id}/respond] Notification failed to dispatch: {email_err}")

    logger.info(f"[/rtis/{request_id}/respond] Success | request_id={request_id} | tracking_id={tracking_id}")
    return RespondResponse(
        request_id=request_id,
        tracking_id=tracking_id,
        status="completed",
        message="Response successfully submitted and citizen notified."
    )

