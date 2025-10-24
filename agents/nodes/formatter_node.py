"""
formatter_node.py
-----------------
Node responsible for converting a raw user query into a polished
RTI letter ready for submission.
"""

from typing import Dict, Any
from agents.base.base_agent import BaseAgent
from utils.logger import logger
from utils.exception_handler import exception_handler
from utils.helpers import load_prompt


class FormatterNode(BaseAgent):
    """
    Formatter Node: transforms informal user queries into formal RTI letters
    """

    def __init__(self):
        super().__init__(agent_name="FormatterNode")
        self.prompt_template = load_prompt("formatter")

    @exception_handler
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Steps:
        1. Retrieve query_text from context
        2. Generate formal RTI query using LLM
        3. Store formatted query in memory
        4. Return formal_query
        """

        # Step 1: Retrieve raw query
        query_text = context.get("query_text")
        if not query_text:
            raise ValueError("No query_text found in context for FormatterNode")

        logger.info(f"[FormatterNode] Formatting raw query: {query_text}")

        # Step 2: Prepare prompt for LLM
        prompt = self.prompt_template.format(query=query_text)

        # Step 3: Call Groq/Gemini LLM to generate formal RTI query
        llm_response = self.call_groq(prompt)
        logger.info(f"[FormatterNode] LLM response: {llm_response}")

        # Step 4: Save in memory
        self.save_memory("last_formal_query", llm_response)

        # Step 5: Return result
        result = {
            "formal_query": llm_response
        }

        logger.info(f"[FormatterNode] Formal query ready.")
        return result
