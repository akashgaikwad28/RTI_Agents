"""
formatter_chain.py
------------------
LangChain pipeline for formatting RTI queries
- Uses prompt templates
- Calls LLMs (Groq, Gemini, or OpenAI)
- Returns polished RTI letters
"""

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI  # Can swap with any LLM
from utils.logger import logger
from utils.exception_handler import exception_handler
from utils.helpers import load_prompt


class FormatterChain:
    """
    Reusable Formatter Chain using LangChain
    """

    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.7):
        self.model_name = model_name
        self.temperature = temperature

        # Load prompt template
        prompt_text = load_prompt("formatter_prompt.txt")
        self.prompt = PromptTemplate(
            input_variables=["query"],
            template=prompt_text
        )

        # Initialize LLM
        self.llm = ChatOpenAI(model_name=self.model_name, temperature=self.temperature)
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

        logger.info(f"🧩 FormatterChain initialized with model: {self.model_name}")

    @exception_handler
    def run(self, query: str) -> dict:
        """
        Run the formatter chain
        Steps:
        1. Format query using prompt
        2. Call LLM
        3. Return polished RTI letter
        """

        logger.info(f"[FormatterChain] Formatting query: {query}")

        # Step 1: Run chain
        llm_output = self.chain.run(query=query)
        logger.debug(f"[FormatterChain] Raw LLM output: {llm_output}")

        # Step 2: Return structured result
        result = {
            "formatted_query": llm_output
        }

        logger.info(f"[FormatterChain] Formatted query ready.")
        return result

