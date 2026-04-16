# memory/memory_node.py

from langgraph.graph import StateGraph, END
from memory.memory_manager import MemoryManager

class MemoryNode:
    """
    Node that handles memory operations such as
    saving context, recalling user data, and linking
    between agent sessions.
    """

    def __init__(self):
        self.manager = MemoryManager()

    def save_user_query(self, session_id: str, query: str, classified_department: str):
        """Save user query and classification result."""
        context = {"query": query, "department": classified_department}
        self.manager.save_context(session_id, context)
        self.manager.add_to_vector_memory(query, {"department": classified_department})
        return {"status": "saved", "session_id": session_id}

    def recall_context(self, session_id: str):
        """Retrieve stored user context."""
        return self.manager.load_context(session_id)

    def search_related_context(self, query: str):
        """Search past memory for related queries."""
        return self.manager.search_memory(query)
