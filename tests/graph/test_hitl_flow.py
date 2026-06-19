"""Tests for Human-in-the-Loop (HITL) manual review pauses."""

import pytest
from graph.graph_builder import build_graph

@pytest.fixture
def mock_settings(temp_workspace):
    from unittest.mock import patch
    with patch("config.settings.settings") as mock_set:
        mock_set.CHECKPOINTER_DB = str(temp_workspace / "test_hitl.db")
        yield mock_set

@pytest.mark.asyncio
async def test_hitl_interrupts_at_approval(mock_settings):
    """Ensure that when HITL is enabled, the graph pauses execution before approval_node."""
    graph = build_graph(enable_hitl=True)
    
    state = {
        "request_id": "req_hitl_test",
        "thread_id": "thread_hitl_test",
        "raw_query": "Requesting municipal PWD road details",
        "user_input": {"name": "Akash", "email": "akash@example.com"},
        "workflow_path": []
    }
    
    config = {"configurable": {"thread_id": "thread_hitl_test"}}
    
    # Run the graph; it should run until the interrupt point
    await graph.ainvoke(state, config)
    
    # Retrieve the state snapshot to assert it is paused at approval_node
    state_snapshot = await graph.aget_state(config)
    assert state_snapshot.next == ("approval_node",), "Graph did not interrupt before approval_node as expected!"
