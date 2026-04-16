"""
info_fetcher_node.py
--------------------
Node responsible for fetching RTI information from:
1. Public RTI portal (simulated)
2. Local MongoDB storage (for submitted or cached queries)

Returns:
- info if available
- None if query needs to be submitted
"""

from typing import Dict, Any, Optional
from agents.base.base_agent import BaseAgent
from mcp_clients.mongo_client import MongoDBClient
from utils.logger import logger
from utils.exception_handler import exception_handler
import os
import json


class InfoFetcherNode(BaseAgent):
    """
    InfoFetcherNode: checks if the RTI information is already public or cached.
    """

    def __init__(self):
        super().__init__(agent_name="InfoFetcherNode")
        # Initialize MongoDB wrapper client
        self.mongo_client = MongoDBClient()  
        logger.info("InfoFetcherNode initialized.")

    @exception_handler
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Steps:
        1. Extract formal query from context
        2. Check MongoDB for previously fetched or submitted data
        3. Simulate a check on public RTI portal
        4. Return information if available, otherwise prompt to submit RTI
        """

        # Step 1: Support both run(context) and run(**context)
        context: Dict[str, Any] = args[0] if args and isinstance(args[0], dict) else kwargs
        formal_query: Optional[str] = context.get("formal_query")
        user_id: Optional[str] = context.get("user_id") 

        if not formal_query:
            raise ValueError("No formal query provided in context for InfoFetcherNode.")

        logger.info(f"[InfoFetcherNode] Fetching info for query: {formal_query}")

        # Step 2: Check MongoDB for cached or previously fetched info
        cached_info: Optional[Dict[str, Any]] = self.mongo_client.get_info_by_query(formal_query)
        if cached_info:
            logger.info("[InfoFetcherNode] Info found in local MongoDB.")
            self.save_memory("last_info_fetch", cached_info)
            return {
                "status": "available",
                "source": "database",
                "info": cached_info
            }

        # Step 3: Simulate public RTI portal check
        logger.info("[InfoFetcherNode] Info not found in DB. Checking public RTI portal (simulated).")
        public_info: Optional[str] = self._simulate_public_portal_check(formal_query)

        if public_info:
            logger.info("[InfoFetcherNode] Info found on public portal.")
            self.save_memory("last_info_fetch", public_info)
            # Cache it in MongoDB for faster future access
            self.mongo_client.save_info(formal_query, public_info)
            return {
                "status": "available",
                "source": "public_portal",
                "info": public_info
            }

        # Step 4: If not found anywhere
        logger.info("[InfoFetcherNode] Info not available publicly. RTI must be submitted.")
        return {
            "status": "not_available",
            "source": "none",
            "info": None
        }

    def _simulate_public_portal_check(self, query: str) -> Optional[str]:
        data_path = os.path.join("data", "public_rti_knowledge.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                simulated_database = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load simulated RTI data: {e}")
            return None

        for key, value in simulated_database.items():
            if key.lower() in query.lower():
                return value
        return None