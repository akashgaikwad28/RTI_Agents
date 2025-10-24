# memory/memory_manager.py

import os
import json
from langchain.memory import ConversationBufferMemory
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config.settings import Settings
from utils.logger import get_logger
from utils.exception_handler import exception_handler

logger = get_logger(__name__)
settings = Settings()

class MemoryManager:
    """
    Central memory manager for all agents.
    Handles both in-memory and persistent vector-based memory using FAISS.
    """

    def __init__(self, persist_path: str = "memory/memory_store"):
        self.persist_path = persist_path
        os.makedirs(self.persist_path, exist_ok=True)

        # Initialize Gemini embeddings
        # try:
        #     self.embedding = GoogleGenerativeAIEmbeddings(
        #         model="models/embedding-001",
        #         google_api_key=settings.GEMINI_API_KEY
        #     )
        #     logger.info("✅ Gemini embeddings initialized successfully.")
        # except Exception as e:
        #     logger.error(f"❌ Failed to initialize Gemini embeddings: {e}")
        #     raise

        # Initialize FAISS vectorstore
        # self.vectorstore = None
        # self._init_vectorstore()

    # @exception_handler
    # def _init_vectorstore(self):
    #     """Load or create FAISS vectorstore for long-term memory."""
    #     try:
    #         self.vectorstore = FAISS.load_local(
    #             self.persist_path,
    #             self.embedding,
    #             allow_dangerous_deserialization=True
    #         )
    #         logger.info("✅ FAISS vectorstore loaded from disk.")
    #     except Exception as e:
    #         logger.warning(f"⚠️ FAISS load failed, creating new store: {e}")
    #         self.vectorstore = FAISS.from_texts(["Initial memory vector"], self.embedding)
    #         self.vectorstore.save_local(self.persist_path)
    #         logger.info("✅ FAISS vectorstore initialized and saved.")

    def get_conversation_memory(self, session_id: str) -> ConversationBufferMemory:
        """Return buffer memory for a given session."""
        logger.debug(f"Creating buffer memory for session: {session_id}")
        return ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    @exception_handler
    def save_context(self, key: str, data: dict):
        """Persist context data locally as JSON."""
        file_path = os.path.join(self.persist_path, f"{key}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"✅ Context saved: {file_path}")

    @exception_handler
    def load_context(self, key: str) -> dict:
        """Load context data from disk."""
        file_path = os.path.join(self.persist_path, f"{key}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                logger.info(f"✅ Context loaded: {file_path}")
                return json.load(f)
        logger.warning(f"⚠️ Context file not found: {file_path}")
        return {}

    @exception_handler
    def add_to_vector_memory(self, text: str, metadata: dict = None):
        """Add new memory to FAISS vectorstore."""
        self.vectorstore.add_texts([text], metadatas=[metadata or {}])
        self.vectorstore.save_local(self.persist_path)
        logger.info(f"✅ Memory added to vectorstore: {text[:50]}...")

    @exception_handler
    def search_memory(self, query: str, k: int = 3) -> list:
        """Retrieve top-k relevant memories using similarity search."""
        results = self.vectorstore.similarity_search(query, k=k)
        logger.info(f"🔍 Memory search completed for query: {query}")
        return [r.page_content for r in results]
    
    
    @exception_handler
    def save(self, agent: str, key: str, value: str):
        """Generic save method for agents to persist memory."""
        data = {"agent": agent, "key": key, "value": value}
        self.save_context(f"{agent}_{key}", data)
        logger.info(f"💾 Memory saved for agent '{agent}' with key '{key}'")
