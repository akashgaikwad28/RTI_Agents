"""
graph_manager.py
----------------
Manages LangGraph workflow for RTI Agents:
- Adds nodes (classifier, formatter, info_fetcher, tracker)
- Registers agents dynamically
- Handles execution flow
- Integrates logging, memory, and exception handling
"""

from typing import Any, Dict, Optional, get_type_hints
from utils.logger import logger
from utils.exception_handler import exception_handler
from agents.nodes.classifier_node import ClassifierNode
from agents.nodes.formatter_node import FormatterNode
from agents.nodes.info_fetcher_node import InfoFetcherNode
from agents.nodes.tracker_node import TrackerNode
from memory.memory_manager import MemoryManager
import inspect


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
        Executes a registered agent's run method with flexible context.
        Detects whether the agent expects `context` or `**kwargs`.
        """
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent '{agent_name}' not found in GraphManager.")

        # Filter context for formatter
        if agent_name == "formatter":
            filtered_context = {"query_text": context.get("query_text", "")}
        else:
            filtered_context = context

        logger.info(f"🚀 Running agent: {agent_name} with keys: {list(filtered_context.keys())}")

        # Detect agent run() signature dynamically
        try:
            sig = inspect.signature(agent.run)
            params = list(sig.parameters.values())

            # Case 1: expects (self, context)
            if len(params) == 2 and params[1].annotation in (Dict[str, Any], dict):
                return agent.run(filtered_context)

            # Case 2: expects (self, **kwargs)
            elif any(p.kind == inspect.Parameter.VAR_KEYWORD for p in params):
                return agent.run(**filtered_context)

            # Default fallback
            else:
                return agent.run(filtered_context)

        except Exception as e:
            logger.error(f"⚠️ Error while running agent '{agent_name}': {e}")
            # safe fallback call
            try:
                return agent.run(filtered_context)
            except Exception:
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
        User Input → Translator → Classifier → Formatter → Info Fetcher → Tracker
        """
        logger.info("🚀 Running RTI workflow in GraphManager.")
        context = dict(user_input)

        # Step 1: Classifier
        logger.info("🔹 Running Classifier Node")
        classification_result = self.nodes['classifier'].run(context)
        context.update(classification_result)

        # Step 2: Formatter
        logger.info("🔹 Running Formatter Node")
        formatted_result = self.nodes['formatter'].run(context)
        context.update(formatted_result)

        # Step 3: Info Fetcher
        logger.info("🔹 Running InfoFetcher Node")
        info_result = self.nodes['info_fetcher'].run(context)
        context.update(info_result)

        # Step 4: Tracker
        logger.info("🔹 Running Tracker Node")
        tracker_result = self.nodes['tracker'].run(context)
        context.update(tracker_result)

        logger.info("✅ RTI workflow completed successfully.")
        return context
