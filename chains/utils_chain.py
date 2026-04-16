# chains/utils_chain.py

"""
Utility Chains
--------------
Reusable micro-chains for summarization, extraction, and context cleaning.
These chains can be used by any agent (formatter, classifier, etc.)
"""

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from mcp_clients.groq_client import get_groq_llm
from utils.logger import get_logger
from utils.exception_handler import safe_execute

logger = get_logger(__name__)

class UtilsChain:
    """Collection of utility LLM chains."""

    def __init__(self):
        try:
            self.llm = get_groq_llm(model="mixtral-8x7b")
            self.summary_prompt = PromptTemplate(
                input_variables=["text"],
                template=(
                    "Summarize the following text clearly and concisely in under 150 words. "
                    "Preserve key entities, facts, and dates:\n\n{text}"
                ),
            )
            self.clean_prompt = PromptTemplate(
                input_variables=["raw_text"],
                template=(
                    "Clean and normalize the following text by removing unnecessary symbols, "
                    "fixing formatting, and improving readability:\n\n{raw_text}"
                ),
            )

            self.summary_chain = LLMChain(llm=self.llm, prompt=self.summary_prompt)
            self.clean_chain = LLMChain(llm=self.llm, prompt=self.clean_prompt)
        except Exception as e:
            logger.error(f"Failed to initialize UtilsChain: {e}")
            raise

    @safe_execute
    def summarize(self, text: str) -> str:
        """Summarize long text while keeping important information."""
        logger.debug("Running summarization utility chain.")
        return self.summary_chain.invoke({"text": text}).get("text", "")

    @safe_execute
    def clean_text(self, raw_text: str) -> str:
        """Clean up and normalize text."""
        logger.debug("Running text cleaning utility chain.")
        return self.clean_chain.invoke({"raw_text": raw_text}).get("text", "")
