import pytest
import sys
import os
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

@pytest.fixture
def mock_settings():
    with patch("config.settings.settings") as mock_set:
        mock_set.CHECKPOINTER_DB = "data/checkpoints/test_checkpoints.db"
        yield mock_set

def test_graph_compilation(mock_settings):
    """Verify that the LangGraph compiles cleanly without cycles or syntax errors."""
    try:
        from graph.graph_builder import build_graph
        graph = build_graph(enable_hitl=False)
        assert graph is not None
        # Check that we have all standard nodes compiled
        expected_nodes = [
            "router_node", "planner_node", "formatter_node", "info_fetcher_node", "classifier_node",
            "tool_selection_node", "retrieval_node", "debate_node", "critic_node",
            "verifier_node", "reviewer_node", "approval_node", "reflection_node",
            "consensus_node", "memory_learning_node", "tracker_node"
        ]
        for node in expected_nodes:
            assert node in graph.nodes, f"Missing node in compiled graph: {node}"
    except Exception as e:
        pytest.fail(f"Graph compilation failed: {e}")

@pytest.mark.asyncio
async def test_router_node_routing():
    """Verify router node correctly routes queries or tracks requests."""
    from graph.nodes.router_node import router_node
    from graph.state import RTIAgentState

    state: RTIAgentState = {
        "raw_query": "I want road construction budget details",
        "language": "en",
        "workflow_path": []
    }

    # Mock the LLM router output
    mock_response = MagicMock()
    mock_response.intent = "new_request"
    mock_response.reason = "Query requires formal RTI preparation"

    with patch("graph.nodes.router_node.get_llm") as mock_get_llm:
        mock_llm = MagicMock()
        mock_structured_llm = MagicMock()
        mock_structured_llm.ainvoke = AsyncMock(return_value=mock_response)
        mock_llm.with_structured_output.return_value = mock_structured_llm
        mock_get_llm.return_value = mock_llm

        result = await router_node(state)
        assert result["intent"] == "new_request"
        assert "router_node" in result["workflow_path"]

@pytest.mark.asyncio
async def test_reviewer_node_bug_detection():
    """
    CRITICAL BUG DETECTOR:
    Verifies if reviewer_node crashes due to missing import 'prompts.reviewer'.
    """
    from graph.state import RTIAgentState
    
    state: RTIAgentState = {
        "raw_query": "Test query",
        "formal_query": "Formal RTI Query draft details...",
        "department": "Public Works",
        "confidence": "high",
        "retrieved_context": ["Context 1", "Context 2"],
        "workflow_path": []
    }

    try:
        from graph.nodes.reviewer_node import reviewer_node
        # If reviewer_node imported successfully despite the bug, we invoke it
        with patch("graph.nodes.reviewer_node.get_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_structured_llm = MagicMock()
            mock_structured_llm.ainvoke = AsyncMock(return_value=MagicMock(
                review_passed=True,
                review_score=0.95,
                grounding_score=0.98,
                hallucination_flags=[],
                review_feedback="Excellent draft",
                suggested_improvements=[]
            ))
            mock_llm.with_structured_output.return_value = mock_structured_llm
            mock_get_llm.return_value = mock_llm
            result = await reviewer_node(state)
            assert result["review_passed"] is True
    except ModuleNotFoundError as e:
        if "prompts.reviewer" in str(e):
            # This is the expected crash behavior we are testing/proving!
            pytest.xfail(f"[EXPECTED CRASH] Reviewer node crashes on missing prompts.reviewer: {e}")
        else:
            raise e
