# info_fetcher_agent.py - auto-generated
"""
info_fetcher_agent.py
---------------------
High-level RTI Info Fetcher Agent
- Uses InfoFetcherNode internally
- Checks if RTI information is publicly available
- Handles logging, exceptions, and memory
"""

from typing import Dict, Any
from agents.base.base_agent import BaseAgent
from agents.nodes.info_fetcher_node import InfoFetcherNode
from utils.logger import logger
from utils.exception_handler import exception_handler


class InfoFetcherAgent(BaseAgent):
    """
    InfoFetcherAgent: orchestrates InfoFetcherNode
    """

    def __init__(self):
        super().__init__(agent_name="InfoFetcherAgent")
        self.node = InfoFetcherNode()
        logger.info("🧩 InfoFetcherAgent initialized.")

    @exception_handler
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """
        High-level method to fetch RTI information.

        Supports both:
        - run(context: Dict[str, Any])
        - run(**context)
        """

        # Handle flexible input
        if args and isinstance(args[0], dict):
            context = args[0]
        else:
            context = kwargs

        if not context.get("formal_query"):
            raise ValueError("No formal query provided in context for InfoFetcherAgent.")

        logger.info("[InfoFetcherAgent] Fetching information for formal query...")

        # Step 2: Call Node
        node_result = self.node.run(context)

        # Step 3: Save in memory
        if node_result and node_result.get("info"):
            self.save_memory("last_fetched_info", node_result.get("info"))

        # Step 4: Return result
        logger.info(
            f"[InfoFetcherAgent] Info fetch completed with status: {node_result.get('status', 'unknown')}"
        )
        return node_result or {"status": "error", "info": None}
