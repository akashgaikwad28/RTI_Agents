"""Tests for the autonomous reflection/self-correction loop and its retry limits."""

import pytest
from unittest.mock import MagicMock
from graph.graph_builder import build_graph

class FailingMockStructuredLLM:
    def __init__(self, schema):
        self.schema = schema

    async def ainvoke(self, messages, *args, **kwargs):
        schema_name = self.schema.__name__ if hasattr(self.schema, "__name__") else str(self.schema)
        
        if "ReviewOutput" in schema_name:
            # Force review failures to trigger the self-correction reflection path
            return self.schema(
                review_passed=False,
                review_score=0.3,
                grounding_score=0.2,
                hallucination_flags=["fabricated_facts"],
                review_feedback="Critical hallucination detected. High risk content.",
                suggested_improvements=["Remove incorrect statements"]
            )
        elif "RouterOutput" in schema_name:
            return self.schema(
                intent="new_request",
                reason="Routing to new request"
            )
        elif "ClassificationOutput" in schema_name:
            return self.schema(
                department="Public Works Department",
                sub_department="Roads",
                confidence="high",
                notes="Mocked high confidence"
            )
        else:
            return MagicMock(spec=self.schema)

class FailingMockLLM:
    def with_structured_output(self, schema, *args, **kwargs):
        return FailingMockStructuredLLM(schema)

    async def ainvoke(self, messages, *args, **kwargs):
        # Deterministic mock answers for formatter and reflection
        from tests.mocks.mock_llm import MockLLMResponse
        return MockLLMResponse(
            content='{"reflection_needed": true, "amended_query": "Please correct and rewrite.", "correction_summary": "Hallucination found", "formal_query": "corrected query draft", "rti_template": {}}'
        )

@pytest.fixture
def mock_settings(temp_workspace):
    from unittest.mock import patch
    with patch("config.settings.settings") as mock_set:
        mock_set.CHECKPOINTER_DB = str(temp_workspace / "test_reflection.db")
        yield mock_set

@pytest.mark.asyncio
async def test_reflection_loop_termination(mock_settings, monkeypatch):
    """Verify that the reflection loop terminates and exits to approval_node after exceeding max_retries."""
    # Force get_llm to use FailingMockLLM inside the node namespaces
    failing_llm = FailingMockLLM()
    monkeypatch.setattr("graph.nodes.reviewer_node.get_llm", lambda *args, **kwargs: failing_llm)
    monkeypatch.setattr("graph.nodes.router_node.get_llm", lambda *args, **kwargs: failing_llm)
    monkeypatch.setattr("graph.nodes.classifier_node.get_llm", lambda *args, **kwargs: failing_llm)
    monkeypatch.setattr("graph.nodes.reflection_node.get_llm", lambda *args, **kwargs: failing_llm)
    
    # Enable reflection loop but disable HITL so it finishes without user interaction
    graph = build_graph(enable_hitl=False)
    
    state = {
        "request_id": "req_loop_test",
        "thread_id": "thread_loop_test",
        "raw_query": "Forced failing query",
        "user_input": {"name": "Akash", "email": "akash@example.com"},
        "workflow_path": [],
        "retry_count": 0,
        "max_retries": 2,
        "approval_status": "approved"
    }
    
    config = {"configurable": {"thread_id": "thread_loop_test"}}
    result = await graph.ainvoke(state, config)
    
    # Assertions:
    # 1. We did visit reflection_node
    reflection_visits = [node for node in result["workflow_path"] if "reflection_node" in node]
    assert len(reflection_visits) > 0
    
    # 2. Retry count was incremented and hit the max
    assert result["retry_count"] == 2
    
    # 3. Traversal completed by breaking the loop and routing to tracker_node
    assert "tracker_node" in result["workflow_path"]
