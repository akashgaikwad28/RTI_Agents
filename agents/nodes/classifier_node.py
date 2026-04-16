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
import json


class ClassifierNode(BaseAgent):
    """
    Classifier Node: converts raw user queries into formal queries and predicts department
    """

    def __init__(self):
        super().__init__(agent_name="ClassifierNode")

        # Load prompt template from file (or fallback default)
        try:
            self.prompt_template = load_prompt("classifier")
        except Exception:
            logger.warning("⚠️ Failed to load prompt from file. Using default inline prompt.")
            self.prompt_template = """
You are an RTI classification assistant. 
Analyze the user's RTI query and return a structured JSON with the department and a more formal version of the query.

Return ONLY JSON in the format below:
{{
    "department": "<department name>",
    "formal_query": "<rewritten, formal version of the RTI query>"
}}

Query: {query}
"""

    @exception_handler
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute classifier logic.
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
        context["translated_query"] = translated_query

        # Step 2: Prepare LLM prompt
        try:
            prompt = self.prompt_template.format(query=translated_query)
        except KeyError as e:
            logger.error(f"[ClassifierNode] Prompt formatting error: {e}. Escaping braces and retrying.")
            safe_prompt = self.prompt_template.replace("{", "{{").replace("}", "}}").replace("{{query}}", "{query}")
            prompt = safe_prompt.format(query=translated_query)

        # Step 3: Call Groq LLM for classification and formalization
        llm_response = self.call_groq(prompt)
        logger.info(f"[ClassifierNode] LLM response: {llm_response}")

        # Step 4: Parse JSON safely
        department = "Unknown"
        formal_query = translated_query

        try:
            response_data = json.loads(llm_response)
            department = response_data.get("department", "Unknown")
            formal_query = response_data.get("formal_query", translated_query)
        except json.JSONDecodeError:
            logger.warning("[ClassifierNode] JSONDecodeError — response is not valid JSON. Using defaults.")
        except Exception as e:
            logger.warning(f"[ClassifierNode] Failed to parse LLM response: {e}")

        # Step 5: Save context in memory
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

        logger.info(f"[ClassifierNode] ✅ Classification result: {result}")
        return result
