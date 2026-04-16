"""
tracker_node.py
---------------
Node responsible for tracking RTI requests
- Generates unique tracking IDs
- Updates request status
- Retrieves status for users
"""

import uuid
from typing import Dict, Any
from agents.base.base_agent import BaseAgent
from mcp_clients.mongo_client import MongoClient
from utils.logger import logger
from utils.exception_handler import exception_handler

class TrackerNode(BaseAgent):
    """
    TrackerNode: handles RTI request tracking
    """

    def __init__(self):
        super().__init__(agent_name="TrackerNode")
        self.mongo_client = MongoClient()
        logger.info("🧩 TrackerNode initialized.")

    @exception_handler
    def run(self, rti_id: str, user_query: str) -> Dict[str, Any]:
        """
        Default run method to comply with BaseAgent contract.
        Delegates to get_status().
        """
        logger.info(f"[TrackerNode] Running tracker for RTI ID: {rti_id} | Query: {user_query}")
        return self.get_status(tracking_id=rti_id)

    @exception_handler
    def create_tracking_id(self, context: Dict[str, Any]) -> str:
        """
        Generate a unique tracking ID for a new RTI request
        - Save request with 'pending' status in MongoDB
        """
        user_data = context.get("user_data")
        formatted_query = context.get("formatted_query")

        if not user_data or not formatted_query:
            raise ValueError("Missing user_data or formatted_query in context for TrackerNode.")

        tracking_id = str(uuid.uuid4())
        logger.info(f"[TrackerNode] Generated tracking ID: {tracking_id}")

        request_record = {
            "tracking_id": tracking_id,
            "user_data": user_data,
            "formatted_query": formatted_query,
            "status": "pending"
        }

        self.mongo_client.save_rti_request(request_record)
        logger.info(f"[TrackerNode] RTI request saved with tracking ID: {tracking_id}")

        self.save_memory("last_tracking_id", tracking_id)
        return tracking_id

    @exception_handler
    def update_status(self, tracking_id: str, status: str) -> Dict[str, Any]:
        """
        Update the status of an existing RTI request
        """
        if not tracking_id or not status:
            raise ValueError("tracking_id and status must be provided to update status.")

        updated = self.mongo_client.update_rti_status(tracking_id, status)
        if updated:
            logger.info(f"[TrackerNode] Status updated for {tracking_id} -> {status}")
            self.save_memory("last_status_update", {"tracking_id": tracking_id, "status": status})
            return {"tracking_id": tracking_id, "status": status}
        else:
            logger.warning(f"[TrackerNode] Tracking ID {tracking_id} not found.")
            return {"tracking_id": tracking_id, "status": "not_found"}

    @exception_handler
    def get_status(self, tracking_id: str) -> Dict[str, Any]:
        """
        Retrieve the current status of an RTI request
        """
        if not tracking_id:
            raise ValueError("tracking_id must be provided to get status.")

        request = self.mongo_client.get_rti_request(tracking_id)
        if request:
            logger.info(f"[TrackerNode] Retrieved status for {tracking_id}: {request.get('status')}")
            return {"tracking_id": tracking_id, "status": request.get("status")}
        else:
            logger.warning(f"[TrackerNode] Tracking ID {tracking_id} not found.")
            return {"tracking_id": tracking_id, "status": "not_found"}
