"""Tests for state restoration and resuming graph execution from a SQLite checkpointer."""

import pytest
from graph.graph_builder import build_graph

@pytest.fixture
def mock_settings(temp_workspace):
    from unittest.mock import patch
    with patch("config.settings.settings") as mock_set:
        mock_set.CHECKPOINTER_DB = str(temp_workspace / "test_checkpoint.db")
        yield mock_set

@pytest.mark.asyncio
async def test_graph_state_resume_after_interrupt(mock_settings):
    """Ensure that the state is successfully saved to the checkpointer and can be resumed with updated approval."""
    graph = build_graph(enable_hitl=True)
    
    state = {
        "request_id": "req_resume_test",
        "thread_id": "thread_resume_test",
        "raw_query": "Road budget details 2024",
        "user_input": {"name": "Akash", "email": "akash@example.com"},
        "workflow_path": []
    }
    
    config = {"configurable": {"thread_id": "thread_resume_test"}}
    
    # Run until interrupt
    await graph.ainvoke(state, config)
    
    # Verify interrupt state
    state_snapshot = await graph.aget_state(config)
    assert state_snapshot.next == ("approval_node",)
    
    # Simulate API resume: update state to approved
    await graph.aupdate_state(config, {"approval_status": "approved"}, as_node="approval_node")
    
    # Resume execution
    result = await graph.ainvoke(None, config)
    
    # Verify traversal successfully completed after resuming
    assert "tracker_node" in result["workflow_path"]
    assert result["status"] == "completed"
    assert result["approval_status"] == "approved"
