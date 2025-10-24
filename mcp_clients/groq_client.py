"""
groq_client.py
--------------
Handles interaction with the Groq LLM API using LangChain and LangGraph.
Centralized MCP client for all agents needing reasoning, classification, or generation.
"""

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from utils.logger import logger
from utils.exception_handler import exception_handler
from config.settings import settings


class GroqClient:
    """
    Wrapper around Groq LLM for structured generation and reasoning tasks.
    Supports both (system + user prompt) and single-prompt calls.
    """

    def __init__(self, model_name: str = "llama-3.1-8b-instant", temperature: float = 0.3):
        try:
            self.model_name = model_name
            self.temperature = temperature
            try:
                self.llm = ChatGroq(
                    groq_api_key=settings.GROQ_API_KEY,
                    model=model_name,
                    temperature=temperature,
                )
                logger.info(f"✅ GroqClient initialized with model '{model_name}'")
            except Exception as e:
                logger.warning(f"⚠️ Model '{model_name}' unavailable. Falling back to 'llama-3.1-70b-versatile'")
                self.llm = ChatGroq(
                    groq_api_key=settings.GROQ_API_KEY,
                    model="llama-3.1-70b-versatile",
                    temperature=temperature,
                )
        except Exception as e:
            logger.error(f"❌ Error initializing GroqClient: {e}")
            raise


    @exception_handler
    def generate(self, user_prompt: str, system_prompt: str = None, temperature: float = None) -> str:
        """
        Generates a response using system + user prompt context.
        Can also be used with a single user prompt.
        """
        try:
            # Use provided temperature or default
            temp = temperature if temperature is not None else self.temperature

            # Build messages dynamically
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=user_prompt))

            logger.info("🤖 GroqClient: Generating response from Groq API...")
            try:
                response = self.llm.invoke(messages, temperature=temp)
            except TypeError:
                # Fallback for versions not supporting temperature
                response = self.llm.invoke(messages)

            # Extract output safely
            output = getattr(response, "content", str(response)).strip()
            logger.info("✅ GroqClient: Response successfully generated.")
            return output

        except Exception as e:
            logger.error(f"❌ GroqClient.generate failed: {e}")
            raise

    def get_llm(self):
        """Returns raw LLM instance for LangChain integrations."""
        return self.llm


# Singleton-style client instance
groq_client = GroqClient()


# Utility function for external chains
def get_groq_llm(model: str = "llama-3-70b", temperature: float = 0.3):
    """Create a fresh ChatGroq instance for ad-hoc chains."""
    return ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model=model,
        temperature=temperature,
    )
