# gemini_client.py - auto-generated
"""
gemini_client.py
----------------
Handles interaction with Google's Gemini model using LangChain.
This acts as an MCP client for AI agents that require summarization,
rewriting, translation, or contextual reasoning capabilities.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage
from utils.logger import logger
from utils.exception_handler import exception_handler
from config.settings import settings


class GeminiClient:
    """
    Wrapper around the Google Gemini model for generative tasks.
    Provides consistent structure and centralized logging.
    """

    def __init__(self, model_name: str = "gemini-1.5-pro", temperature: float = 0.4):
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=settings.GOOGLE_API_KEY,
                temperature=temperature,
            )
            logger.info(f"✅ GeminiClient initialized with model '{model_name}'")
        except Exception as e:
            logger.error(f"❌ Error initializing GeminiClient: {e}")
            raise

    @exception_handler
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates a structured response from Gemini given a system and user prompt.
        """
        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ]

            response = self.llm.invoke(messages)
            output = response.content.strip() if hasattr(response, "content") else str(response)
            logger.info("🤖 GeminiClient: Response successfully generated.")
            return output

        except Exception as e:
            logger.error(f"❌ GeminiClient.generate failed: {e}")
            raise


# Singleton instance for shared usage
gemini_client = GeminiClient()
