"""Tests for RTIAgentState schema integrity and preventing schema drift."""

import pytest
from graph.graph_builder import build_graph
from graph.state import RTIAgentState

@pytest.fixture
def mock_settings(temp_workspace):
    from unittest.mock import patch
    with patch("config.settings.settings") as mock_set:
        mock_set.CHECKPOINTER_DB = str(temp_workspace / "test_integrity.db")
        yield mock_set

@pytest.mark.asyncio
async def test_state_integrity_during_execution(mock_settings):
    """Ensure that the state maintains schema integrity and all required keys conform to RTIAgentState TypedDict."""
    graph = build_graph(enable_hitl=False)
    
    state = {
        "request_id": "req_integrity_1",
        "thread_id": "thread_integrity_1",
        "raw_query": "Road budget Pune",
        "user_input": {"name": "Akash", "email": "akash@example.com"},
        "workflow_path": [],
        "approval_status": "approved"
    }
    
    config = {"configurable": {"thread_id": "thread_integrity_1"}}
    result = await graph.ainvoke(state, config)
    
    # Assert that all keys present in the final state are declared in RTIAgentState
    declared_keys = RTIAgentState.__annotations__.keys()
    
    for key in result.keys():
        assert key in declared_keys, f"Schema drift detected! Key '{key}' in output state is not defined in RTIAgentState annotation."
        
    # Assert essential fields are correctly typed
    assert isinstance(result["request_id"], str)
    assert isinstance(result["thread_id"], str)
    assert isinstance(result["workflow_path"], list)
    assert isinstance(result["status"], str)
    assert isinstance(result["tracking_id"], str)
