"""
graph_manager.py
----------------
Manages LangGraph workflow for RTI Agents:
- Adds nodes (classifier, formatter, info_fetcher, tracker)
- Handles execution flow
- Integrates logging, memory, and exception handling
"""

from typing import Any, Dict, Optional
from utils.logger import logger
from utils.exception_handler import exception_handler
from agents.nodes.classifier_node import ClassifierNode
from agents.nodes.formatter_node import FormatterNode
from agents.nodes.info_fetcher_node import InfoFetcherNode
from agents.nodes.tracker_node import TrackerNode
from memory.memory_manager import MemoryManager

class GraphManager:
    """
    Orchestrates all nodes for RTI processing
    """

    def __init__(self):
        self.nodes = {}
        self.memory = MemoryManager()
        self._initialize_nodes()
        logger.info("🧩 GraphManager initialized with nodes.")

    def _initialize_nodes(self):
        """Initialize all nodes and add to graph"""
        self.nodes['classifier'] = ClassifierNode()
        self.nodes['formatter'] = FormatterNode()
        self.nodes['info_fetcher'] = InfoFetcherNode()
        self.nodes['tracker'] = TrackerNode()
        logger.info("✅ Nodes initialized: " + ", ".join(self.nodes.keys()))

    @exception_handler
    def run_workflow(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the full workflow:
        User Input → Translator (inside agent) → Classifier → Formatter → Info Fetcher → Tracker
        """
        logger.info("🚀 Running RTI workflow in GraphManager.")

        context = {}
        context.update(user_input)  # initial user input

        # Step 1: Classifier
        logger.info("🔹 Running Classifier Node")
        classification_result = self.nodes['classifier'].run(context)
        context['department'] = classification_result.get('department')
        context['formal_query'] = classification_result.get('formal_query')
        context['raw_query'] = classification_result.get('raw_query')

        # Step 2: Formatter
        logger.info("🔹 Running Formatter Node")
        formatted_result = self.nodes['formatter'].run(context)
        context['formatted_query'] = formatted_result.get('formatted_query')

        # Step 3: Info Fetcher
        logger.info("🔹 Running InfoFetcher Node")
        info_result = self.nodes['info_fetcher'].run(context)
        context['info_available'] = info_result.get('info_available')
        context['info_data'] = info_result.get('info_data')

        # Step 4: Tracker
        logger.info("🔹 Running Tracker Node")
        tracker_result = self.nodes['tracker'].run(context)
        context['tracking_id'] = tracker_result.get('tracking_id')
        context['status'] = tracker_result.get('status')

        logger.info("✅ RTI workflow completed successfully.")
        return context

    @exception_handler
    def add_node(self, node_name: str, node_object):
        """Add a new node dynamically"""
        self.nodes[node_name] = node_object
        logger.info(f"➕ Node added dynamically: {node_name}")

    @exception_handler
    def get_node(self, node_name: str):
        """Retrieve a node by name"""
        return self.nodes.get(node_name, None)
