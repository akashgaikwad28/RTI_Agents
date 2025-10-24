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
    def run(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        High-level method to classify user query
        Steps:
        1. Validate input
        2. Call classifier node
        3. Store results in memory
        4. Return classification results
        """

        # Step 1: Validate input
        if not user_data.get("query"):
            raise ValueError("User query is missing in input.")

        logger.info(f"[ClassifierAgent] Running classification for user: {user_data.get('name')}")

        # Step 2: Call classifier node
        node_result = self.node.run(user_data)

        # Step 3: Store in memory for this agent
        self.save_memory("last_classification", node_result)

        # Step 4: Return result
        logger.info(f"[ClassifierAgent] Classification result: {node_result}")
        return node_result
