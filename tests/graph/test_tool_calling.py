"""Tests for tool selection, parallel calling, and resilient function fallback mappings."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from graph.nodes.tool_selection_node import tool_selection_node
from graph.state import RTIAgentState

@pytest.mark.asyncio
async def test_tool_selection_resilient_fallback():
    """Verify tool selection selects tools and parallel execution gracefully handles tool failures (resilient fallback)."""
    state: RTIAgentState = {
        "request_id": "req_tool_test",
        "formal_query": "road budget details",
        "department": "Public Works Department",
        "selected_tools": ["semantic_retriever", "fake_failing_tool"],
        "tool_results": [],
        "reasoning_trace": [],
        "workflow_path": [],
        "agent_durations": {}
    }
    
    # Mock tool registry to return one success and one failure
    mock_success_result = MagicMock()
    mock_success_result.model_dump.return_value = {"status": "success", "data": "retrieved context"}
    
    mock_registry = MagicMock()
    # execute_tool is an async function
    async def mock_execute(tool_name, *args, **kwargs):
        if tool_name == "fake_failing_tool":
            raise ValueError("Tool connection timeout")
        return mock_success_result

    mock_registry.execute_tool = mock_execute
    
    with patch("graph.nodes.tool_selection_node.get_tool_registry", return_value=mock_registry):
        result = await tool_selection_node(state)
        
        # Verify both tools were executed and serialized into tool_results
        assert len(result["tool_results"]) == 2
        
        # Verify success serialization
        success_result = result["tool_results"][0]
        assert success_result["status"] == "success"
        assert success_result["data"] == "retrieved context"
        
        # Verify resilient error fallback serialization
        error_result = result["tool_results"][1]
        assert error_result["status"] == "error"
        assert "Tool connection timeout" in error_result["error"]
        
        # Verify reasoning trace and workflow path
        assert "tool_selection_node" in result["workflow_path"]
        assert len(result["selected_tools"]) == 2
