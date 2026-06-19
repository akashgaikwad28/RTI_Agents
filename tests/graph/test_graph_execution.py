"""Tests for full end-to-end graph execution."""

import pytest
from graph.graph_builder import build_graph
from graph.state import RTIAgentState

@pytest.fixture
def mock_settings():
    from unittest.mock import patch
    with patch("config.settings.settings") as mock_set:
        mock_set.CHECKPOINTER_DB = "data/checkpoints/test_checkpoints.db"
        yield mock_set

@pytest.mark.asyncio
async def test_end_to_end_graph_traversal(mock_settings):
    """Verify end-to-end graph compilation and traversal through routing, formulation, classification, and tracking."""
    # Build graph without HITL to allow full traversal to tracking
    graph = build_graph(enable_hitl=False)
    
    state: RTIAgentState = {
        "request_id": "test_req_123",
        "thread_id": "test_thread_123",
        "raw_query": "I want to request road construction budget details of Pune municipality for 2024.",
        "user_input": {
            "name": "Akash",
            "email": "akash@example.com",
            "address": "Pune",
            "state": "Maharashtra",
            "district": "Pune"
        },
        "workflow_path": [],
        "agent_durations": {},
        "llm_models_used": {},
        "tools_used": [],
        "approval_status": "approved"
    }
    
    config = {"configurable": {"thread_id": "test_thread_123"}}
    result = await graph.ainvoke(state, config)
    
    # Assertions to verify correct workflow path traversal
    assert "router_node" in result["workflow_path"]
    assert "formatter_node" in result["workflow_path"]
    assert "classifier_node" in result["workflow_path"]
    assert "tracker_node" in result["workflow_path"]
    assert result["status"] == "completed"
    assert "tracking_id" in result
    assert result["tracking_id"].startswith("RTI-")
    assert "final_response" in result
