import asyncio
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from dotenv import load_dotenv
env_path = os.path.join(PROJECT_ROOT, ".env")
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv(dotenv_path=os.path.join(PROJECT_ROOT, ".env.example"))

# Set mock API keys so LLM routing won't crash even if key is missing/dummy
os.environ["GROQ_API_KEY"] = os.environ.get("GROQ_API_KEY") or "gsk_dummykey123456789012345678901234"
os.environ["GEMINI_API_KEY"] = os.environ.get("GEMINI_API_KEY") or "AIzaSyDummyKey_12345678901234567890"

from graph.state import RTIAgentState
from config.settings import settings
from langgraph.graph import START, END, StateGraph
from graph.nodes.router_node import router_node
from graph.nodes.planner_node import planner_node
from graph.nodes.formatter_node import formatter_node
from graph.nodes.info_fetcher_node import info_fetcher_node
from graph.nodes.classifier_node import classifier_node
from graph.nodes.tracker_node import tracker_node
from graph.router import route_after_router, route_after_info_fetcher

async def verify_interception():
    print("Initializing verification...")
    
    # Construct a local test graph compiled WITHOUT checkpointer to avoid database requirements
    builder = StateGraph(RTIAgentState)
    builder.add_node("router_node", router_node)
    builder.add_node("planner_node", planner_node)
    builder.add_node("formatter_node", formatter_node)
    builder.add_node("info_fetcher_node", info_fetcher_node)
    builder.add_node("classifier_node", classifier_node)
    builder.add_node("tracker_node", tracker_node)
    
    builder.add_edge(START, "router_node")
    builder.add_conditional_edges("router_node", route_after_router, {"planner_node": "planner_node", "tracker_node": "tracker_node"})
    builder.add_edge("planner_node", "formatter_node")
    builder.add_edge("formatter_node", "info_fetcher_node")
    builder.add_conditional_edges("info_fetcher_node", route_after_info_fetcher, {"tracker_node": "tracker_node", "classifier_node": "classifier_node"})
    builder.add_edge("tracker_node", END)
    
    graph = builder.compile()
    
    # Define a query that should be intercepted based on data/public_rti_knowledge.json
    state: RTIAgentState = {
        "request_id": "test-request-id",
        "thread_id": "test-thread-id",
        "session_id": "test-session-id",
        "user_input": {
            "name": "Test User",
            "email": "test@example.com",
            "address": "Pune, Maharashtra",
            "query_text": "Can you provide details about the local agriculture schemes?"
        },
        "raw_query": "Can you provide details about the local agriculture schemes?",
        "language": "en",
        "uploaded_documents": [],
        "conversation_history": [],
        "active_request_id": "",
        "translated_query": "",
        "sanitized_query": "Can you provide details about the local agriculture schemes?",
        "formal_query": "Can you provide details about the local agriculture schemes?",
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
        "approval_required": False,
        "approval_status": "approved",
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

    config = {"configurable": {"thread_id": "test-thread-id"}}

    from unittest.mock import AsyncMock, MagicMock, patch
    
    # Mock the LLM router output to guarantee "new_request" intent
    mock_response = MagicMock()
    mock_response.intent = "new_request"
    mock_response.reason = "Query requires formal RTI preparation"

    with patch("graph.nodes.router_node.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_structured_llm = MagicMock()
        mock_structured_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm.with_structured_output.return_value = mock_structured_llm
        mock_get_llm.return_value = mock_llm
        
        print("Invoking graph...")
        result = await graph.ainvoke(state, config=config)
    
    print("\n--- GRAPH OUTPUT ---")
    print(f"Workflow Path: {result.get('workflow_path')}")
    print(f"Info Available: {result.get('info_available')}")
    print(f"Status: {result.get('status')}")
    print(f"Tracking ID: {result.get('tracking_id')}")
    print(f"Final Response:\n{result.get('final_response').replace('ℹ️', '[INFO]')}")
    
    # Assertions to verify correct routing and interception
    assert result.get("info_available") is True, "Interception failed: info_available is not True!"
    assert result.get("status") == "completed", "Status is not completed!"
    assert "info_fetcher_node" in result.get("workflow_path"), "info_fetcher_node was not visited!"
    assert "classifier_node" not in result.get("workflow_path"), "Interception failed: classifier_node was visited!"
    assert "tracker_node" in result.get("workflow_path"), "tracker_node was not visited!"
    
    print("\n[SUCCESS] Verification Successful: Query intercepted, heavy pipeline routed around, resolved cleanly!")

if __name__ == "__main__":
    asyncio.run(verify_interception())
