# groq_client.py - auto-generated
"""
groq_client.py
----------------
Handles interaction with the Groq LLM API using LangChain and LangGraph.
This acts as a centralized MCP client for all AI agents that need reasoning,
classification, or text-generation capabilities.
"""

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from utils.custom_logger import logger
from utils.exception_handler import exception_handler
from config.settings import settings


class GroqClient:
    """
    A wrapper around the Groq LLM for handling all text generation and reasoning tasks.
    """

    def __init__(self, model_name: str = "llama-3.1-70b-versatile", temperature: float = 0.3):
        try:
            self.llm = ChatGroq(
                groq_api_key=settings.GROQ_API_KEY,
                model=model_name,
                temperature=temperature,
            )
            logger.info(f"✅ GroqClient initialized with model '{model_name}'")
        except Exception as e:
            logger.error(f"❌ Error initializing GroqClient: {e}")
            raise

    @exception_handler
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates a response from the Groq model based on system and user prompts.
        """
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]

            response = self.llm.invoke(messages)
            output = response.content.strip() if hasattr(response, "content") else str(response)
            logger.info("🤖 GroqClient: Response successfully generated.")
            return output

        except Exception as e:
            logger.error(f"❌ GroqClient.generate failed: {e}")
            raise


# Singleton-style client instance (for global reuse)
groq_client = GroqClient()
