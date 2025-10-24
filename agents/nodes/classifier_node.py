"""
classifier_node.py
-----------------
Node responsible for classifying raw RTI queries into departments.
Stores both raw and formalized queries for traceability.
"""

from typing import Dict, Any
from agents.base.base_agent import BaseAgent
from utils.logger import logger
from utils.exception_handler import exception_handler
from utils.helpers import load_prompt


class ClassifierNode(BaseAgent):
    """
    Classifier Node: converts raw user queries into formal queries and predicts department
    """

    def __init__(self):
        super().__init__(agent_name="ClassifierNode")
        # Load prompt template from prompts/classifier_prompt.txt
        self.prompt_template = load_prompt("classifier")

    @exception_handler
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute classifier logic
        Steps:
        1. Translate query to English if necessary
        2. Generate formal query using LLM
        3. Predict department using LLM
        4. Store both raw and formal queries
        """

        user_query = context.get("query", "")
        if not user_query:
            raise ValueError("User query is empty in context")

        logger.info(f"[ClassifierNode] Raw query: {user_query}")

        # Step 1: Translate query to English
        translated_query = self.translate_text(user_query, target_lang="en")
        context['translated_query'] = translated_query

        # Step 2: Prepare LLM prompt
        prompt = self.prompt_template.format(query=translated_query)

        # Step 3: Call Groq LLM for classification and formalization
        llm_response = self.call_groq(prompt)
        logger.info(f"[ClassifierNode] LLM response: {llm_response}")

        # Step 4: Extract department & formal query from LLM response
        # For simplicity, assume LLM returns JSON with keys: 'department', 'formal_query'
        try:
            import json
            response_data = json.loads(llm_response)
            department = response_data.get("department", "Unknown")
            formal_query = response_data.get("formal_query", translated_query)
        except Exception:
            logger.warning("[ClassifierNode] Failed to parse LLM response as JSON. Using defaults.")
            department = "Unknown"
            formal_query = translated_query

        # Step 5: Save in memory
        self.save_memory("last_query", user_query)
        self.save_memory("last_formal_query", formal_query)
        self.save_memory("last_department", department)

        # Step 6: Return results
        result = {
            "raw_query": user_query,
            "translated_query": translated_query,
            "formal_query": formal_query,
            "department": department
        }

        logger.info(f"[ClassifierNode] Classification result: {result}")
        return result
