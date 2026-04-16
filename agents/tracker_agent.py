# tracker_agent.py
"""
High-level RTI Tracker Agent
----------------------------
- Manages creation, update, and retrieval of RTI request statuses
- Uses TrackerNode internally
"""

from typing import Dict, Any
from agents.base.base_agent import BaseAgent
from agents.nodes.tracker_node import TrackerNode
from utils.logger import logger
from utils.exception_handler import exception_handler

class TrackerAgent(BaseAgent):
    """
    TrackerAgent: orchestrates TrackerNode operations
    """

    def __init__(self):
        super().__init__(agent_name="TrackerAgent")
        self.node = TrackerNode()
        logger.info("🧩 TrackerAgent initialized.")

    @exception_handler
    def run(self, rti_id: str, user_query: str) -> Dict[str, Any]:
        """
        Required by BaseAgent. Handles generic RTI tracking queries.
        """
        logger.info(f"[TrackerAgent] Running tracker for RTI ID: {rti_id} | Query: {user_query}")
        return self.get_request_status(tracking_id=rti_id)

    @exception_handler
    def create_request(self, context: Dict[str, Any]) -> str:
        """
        Create a new RTI request and generate tracking ID
        """
        logger.info("[TrackerAgent] Creating new RTI request...")
        tracking_id = self.node.create_tracking_id(context)
        self.save_memory("last_tracking_id", tracking_id)
        return tracking_id

    @exception_handler
    def update_request_status(self, tracking_id: str, status: str) -> Dict[str, Any]:
        """
        Update the status of an existing RTI request
        """
        logger.info(f"[TrackerAgent] Updating status for {tracking_id} -> {status}")
        result = self.node.update_status(tracking_id, status)
        self.save_memory("last_status_update", result)
        return result

    @exception_handler
    def get_request_status(self, tracking_id: str) -> Dict[str, Any]:
        """
        Retrieve the current status of an RTI request
        """
        logger.info(f"[TrackerAgent] Retrieving status for {tracking_id}")
        status_info = self.node.get_status(tracking_id)
        self.save_memory("last_status_retrieved", status_info)
        return status_info
