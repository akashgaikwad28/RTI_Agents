# classifier_agent.py - auto-generated
"""
classifier_agent.py
------------------
High-level RTI Classifier Agent
- Uses ClassifierNode internally
- Handles raw user query classification
- Provides easy-to-use interface for GraphManager or API
"""

from typing import Dict, Any
from agents.base.base_agent import BaseAgent
from agents.nodes.classifier_node import ClassifierNode
from utils.logger import logger
from utils.exception_handler import exception_handler

class ClassifierAgent(BaseAgent):
    """
    Classifier Agent: orchestrates the classifier node and provides high-level methods
    """

    def __init__(self):
        super().__init__(agent_name="ClassifierAgent")
        self.node = ClassifierNode()
        logger.info("🧩 ClassifierAgent initialized.")

    @exception_handler
    def run(self, **context) -> Dict[str, Any]:
        """
        Classify the RTI query from user context.
        Accepts flexible keyword arguments from GraphManager.
        """

        
        query = (
            context.get("query")
            or context.get("query_text")
            or context.get("user_query")
            or context.get("rti_query")
            or context.get("message")
        )

        user_name = context.get("name") or "Unknown User"

        if not query:
            raise ValueError("User query is missing in input context.")

        logger.info(f"[ClassifierAgent] Running classification for user: {user_name}")

        
        user_data = {
            "user_id": context.get("user_id"),
            "name": user_name,
            "query": query,
        }

     
        node_result = self.node.run(user_data)

      
        self.save_memory("last_classification", node_result)

      
        logger.info(f"[ClassifierAgent] Classification result: {node_result}")
        return node_result
