"""
classifier_chain.py
------------------
LangChain pipeline for classifying RTI queries
- Uses prompt templates
- Calls LLMs (Groq or Gemini)
- Returns structured output
"""

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI  # Or any other compatible LLM
from utils.logger import logger
from utils.exception_handler import exception_handler
from utils.helpers import load_prompt


class ClassifierChain:
    """
    Reusable classifier chain using LangChain
    """

    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature

        # Load prompt template
        prompt_text = load_prompt("classifier_prompt.txt")
        self.prompt = PromptTemplate(
            input_variables=["query"],
            template=prompt_text
        )

        # Initialize LLM
        self.llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

        logger.info(f"🧩 ClassifierChain initialized with model: {self.model_name}")

    @exception_handler
    def run(self, query: str) -> dict:
        """
        Run the classification chain
        Steps:
        1. Format query using prompt
        2. Call LLM
        3. Parse JSON output
        """

        logger.info(f"[ClassifierChain] Classifying query: {query}")

        # Step 1: Run chain
        llm_output = self.chain.run(query=query)
        logger.debug(f"[ClassifierChain] Raw LLM output: {llm_output}")

        # Step 2: Parse LLM JSON output
        try:
            import json
            result = json.loads(llm_output)
            department = result.get("department", "Unknown")
            formal_query = result.get("formal_query", query)
        except Exception:
            logger.warning("[ClassifierChain] Failed to parse LLM output as JSON. Using defaults.")
            department = "Unknown"
            formal_query = query

        output = {
            "raw_query": query,
            "formal_query": formal_query,
            "department": department
        }

        logger.info(f"[ClassifierChain] Classification result: {output}")
        return output
