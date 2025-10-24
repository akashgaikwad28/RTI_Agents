"""
graph_manager.py
----------------
Manages LangGraph workflow for RTI Agents:
- Adds nodes (classifier, formatter, info_fetcher, tracker)
- Registers agents dynamically
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
    Orchestrates all nodes and agents for RTI processing
    """

    def __init__(self):
        self.nodes: Dict[str, Any] = {}
        self.agents: Dict[str, Any] = {}
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
    def register_agent(self, agent_name: str, agent_object: Any):
        """Register an agent dynamically"""
        self.agents[agent_name] = agent_object
        logger.info(f"✅ Agent registered: {agent_name}")

    @exception_handler
    def get_agent(self, agent_name: str) -> Optional[Any]:
        """Retrieve a registered agent"""
        return self.agents.get(agent_name)

    @exception_handler
    def run_agent(self, agent_name: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a registered agent's run method with minimal context.
        """
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found in GraphManager.")

        # Only pass query_text to formatter
        if agent_name == "formatter":
            filtered_context = {
                "query_text": context.get("query_text", "")
            }
        else:
            filtered_context = context  # pass full context to other agents

        logger.info(f"🚀 Running agent: {agent_name} with keys: {list(filtered_context.keys())}")
        return agent.run(**filtered_context)


    @exception_handler
    def add_node(self, node_name: str, node_object: Any):
        """Add a new node dynamically"""
        self.nodes[node_name] = node_object
        logger.info(f"➕ Node added dynamically: {node_name}")

    @exception_handler
    def get_node(self, node_name: str) -> Optional[Any]:
        """Retrieve a node by name"""
        return self.nodes.get(node_name)

    @exception_handler
    def run_workflow(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the full workflow:
        User Input → Translator (inside agent) → Classifier → Formatter → Info Fetcher → Tracker
        """
        logger.info("🚀 Running RTI workflow in GraphManager.")

        context = {}
        context.update(user_input)

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
