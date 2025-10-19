"""
base_agent.py
-------------
Abstract Base Agent class.
Provides common functionality for all RTI agents:
- Logging
- Exception handling
- LLM and Translator clients
- Memory management (LangGraph / LangChain)
- Utility methods
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from utils.logger import logger
from utils.exception_handler import exception_handler
from mcp_clients import groq_client, gemini_client, translator_client, mongo_client
from memory.memory_manager import MemoryManager


class BaseAgent(ABC):
    """
    Base Agent class to be inherited by all agents (classifier, formatter, tracker, etc.)
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.groq_client = groq_client.groq_client
        self.gemini_client = gemini_client.gemini_client
        self.translator_client = translator_client.translator_client
        self.mongo_client = mongo_client.mongo_client
        self.memory = MemoryManager()
        logger.info(f"🧠 BaseAgent '{self.agent_name}' initialized.")

    @exception_handler
    def call_groq(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Call Groq LLM for generation
        """
        logger.info(f"[{self.agent_name}] Calling Groq LLM...")
        response = self.groq_client.generate(prompt=prompt, temperature=temperature)
        logger.debug(f"[{self.agent_name}] Groq Response: {response}")
        return response

    @exception_handler
    def call_gemini(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Call Gemini (Google GenAI) for generation
        """
        logger.info(f"[{self.agent_name}] Calling Gemini LLM...")
        response = self.gemini_client.generate(prompt=prompt, temperature=temperature)
        logger.debug(f"[{self.agent_name}] Gemini Response: {response}")
        return response

    @exception_handler
    def translate_text(self, text: str, target_lang: str = "en") -> str:
        """
        Translate text using Translator client
        """
        logger.info(f"[{self.agent_name}] Translating text to {target_lang}...")
        translated = self.translator_client.translate(text=text, target_lang=target_lang)
        logger.debug(f"[{self.agent_name}] Translated Text: {translated}")
        return translated

    @exception_handler
    def save_memory(self, key: str, value: Any):
        """
        Save key-value pair in agent memory
        """
        self.memory.save(agent=self.agent_name, key=key, value=value)
        logger.info(f"[{self.agent_name}] Saved to memory: {key}")

    @exception_handler
    def load_memory(self, key: str) -> Optional[Any]:
        """
        Load value from agent memory by key
        """
        value = self.memory.load(agent=self.agent_name, key=key)
        logger.info(f"[{self.agent_name}] Loaded from memory: {key} -> {value}")
        return value

    @abstractmethod
    @exception_handler
    def run(self, *args, **kwargs) -> Any:
        """
        Abstract method to implement agent-specific logic
        """
        raise NotImplementedError(f"{self.agent_name} must implement the run() method.")
