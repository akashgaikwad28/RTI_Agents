"""
formatter_agent.py
------------------
High-level RTI Formatter Agent
- Uses FormatterNode internally
- Converts informal user queries into polished RTI letters
- Handles logging, exceptions, and memory
"""

from typing import Dict, Any
from agents.base.base_agent import BaseAgent
from agents.nodes.formatter_node import FormatterNode
from utils.logger import logger
from utils.exception_handler import exception_handler

class FormatterAgent(BaseAgent):
    """
    Formatter Agent: orchestrates FormatterNode and provides high-level methods
    """

    def __init__(self):
        super().__init__(agent_name="FormatterAgent")
        self.node = FormatterNode()
        logger.info("🧩 FormatterAgent initialized.")

    @exception_handler
    def run(self, query_text: str) -> Dict[str, Any]:
        """
        High-level method to format a raw user query into a formal RTI query.
        Steps:
        1. Validate input
        2. Call FormatterNode
        3. Store formatted query in memory
        4. Return formatted query
        """

        # Step 1: Validate input
        if not query_text or not isinstance(query_text, str):
            raise ValueError("Missing or invalid query_text for FormatterAgent.")

        logger.info("[FormatterAgent] Formatting user query...")

        # Step 2: Call FormatterNode
        context = {"query_text": query_text}
        node_result = self.node.run(context)

        # Step 3: Store in memory
        self.save_memory("last_formatted_query", node_result.get("formatted_query"))

        # Step 4: Return result
        logger.info("[FormatterAgent] Formal RTI query generated.")
        return node_result
