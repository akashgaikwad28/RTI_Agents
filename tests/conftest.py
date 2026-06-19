"""Global pytest fixtures."""

import os
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, AsyncMock

# --- Module-Level Patches to prevent import-time binding bypass ---
import llm_router.llm_router
from tests.mocks.mock_llm import MockLLM
llm_router.llm_router.get_llm = lambda *args, **kwargs: MockLLM()

import mcp_clients.mongo_client

class MockMongoCollection:
    async def update_one(self, filter, update, upsert=False):
        return MagicMock()
    async def insert_one(self, doc):
        return MagicMock(inserted_id="mock_id")
    async def find_one(self, query):
        return {"tracking_id": "RTI-2024-123456", "status": "submitted", "department": "Public Works Department", "created_at": "2026-05-20"}
    def find(self, *args, **kwargs):
        mock_cursor = AsyncMock()
        mock_cursor.sort.return_value = mock_cursor
        mock_cursor.limit.return_value = mock_cursor
        mock_cursor.to_list = AsyncMock(return_value=[])
        return mock_cursor

class MockMongoDB:
    def __init__(self):
        self.collections = {}

    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = MockMongoCollection()
        return self.collections[name]

class MockAsyncMongoClient:
    def __init__(self):
        self.db = MockMongoDB()

_mock_mongo_client = MockAsyncMongoClient()
async def _mock_get_mongo_client():
    return _mock_mongo_client

mcp_clients.mongo_client.get_mongo_client = _mock_get_mongo_client

import tools.notification_tool
async def _mock_send_notification(*args, **kwargs):
    return True

tools.notification_tool.send_submission_notification = _mock_send_notification
tools.notification_tool.send_approval_notification = _mock_send_notification

import rag.embeddings.embedding_router
from tests.mocks.mock_embedder import MockEmbeddingRouter, MockEmbedder
rag.embeddings.embedding_router.get_embedder = lambda: MockEmbeddingRouter()

import rag.vectorstore.faiss_store
rag.vectorstore.faiss_store.get_embedder = lambda: MockEmbeddingRouter()

from langgraph.checkpoint.memory import MemorySaver
import graph.graph_builder
class TestingCheckpointer(MemorySaver):
    def __init__(self, *args, **kwargs):
        super().__init__()
graph.graph_builder.SqliteSaver = TestingCheckpointer
# ------------------------------------------------------------------

from tests.mocks.mock_vectorstore import MockVectorStore
from config.settings import settings

@pytest.fixture(autouse=True)
def mock_env():
    import tempfile
    test_path = os.path.join(tempfile.gettempdir(), "rti_test_faiss")
    os.environ["FAISS_INDEX_PATH"] = test_path
    settings.FAISS_INDEX_PATH = test_path
    
    # Force sqlite/memory checkpointer during testing to bypass live cloud databases
    original_checkpointer_type = settings.CHECKPOINTER_TYPE
    settings.CHECKPOINTER_TYPE = "sqlite"
    
    yield
    
    settings.CHECKPOINTER_TYPE = original_checkpointer_type
    
@pytest.fixture
def mock_embedder():
    return MockEmbedder()
    
@pytest.fixture
def mock_vectorstore():
    return MockVectorStore()
    
@pytest.fixture
def temp_workspace():
    with TemporaryDirectory() as d:
        yield Path(d)



