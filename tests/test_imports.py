import pytest
import sys
import os

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def test_config_settings_imports():
    """Verify config settings import and validate cleanly."""
    try:
        from config.settings import settings
        assert settings is not None
    except Exception as e:
        pytest.fail(f"Failed to import settings: {e}")

def test_observability_imports():
    """Verify structured logger, metrics, and tracing imports."""
    try:
        from observability.structured_logger import get_logger
        from observability.metrics import rti_agent_duration
        from observability.tracing import settings
        assert get_logger is not None
        assert rti_agent_duration is not None
    except Exception as e:
        pytest.fail(f"Observability imports failed: {e}")

def test_mcp_and_rag_imports():
    """Verify MongoDB client and RAG components import cleanly."""
    try:
        from mcp_clients.mongo_client import get_mongo_client
        from rag.vectorstore.faiss_store import get_faiss_store
        from rag.vectorstore.semantic_cache import get_semantic_cache
        assert get_mongo_client is not None
        assert get_faiss_store is not None
        assert get_semantic_cache is not None
    except Exception as e:
        pytest.fail(f"RAG or DB imports failed: {e}")

def test_graph_state_imports():
    """Verify graph state structure imports without serialization/type errors."""
    try:
        from graph.state import RTIAgentState
        assert RTIAgentState is not None
    except Exception as e:
        pytest.fail(f"Graph state import failed: {e}")


