"""
info_fetcher_chain.py
---------------------
LangChain pipeline for fetching RTI information.
- Checks local MongoDB cache
- Optionally queries LLM for hints or suggestions
- Returns structured info availability
"""

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from utils.logger import logger
from utils.exception_handler import exception_handler
from utils.helpers import load_prompt
from mcp_clients.mongo_client import MongoClient

class InfoFetcherChain:
    """
    Reusable InfoFetcher Chain using LangChain
    """

    def __init__(self, use_llm: bool = False, model_name: str = "gpt-3.5-turbo"):
        """
        Args:
            use_llm (bool): If True, will generate suggested info using LLM if not found in DB
            model_name (str): LLM model name for suggestions
        """
        self.use_llm = use_llm
        self.model_name = model_name
        self.mongo_client = MongoClient()

        if self.use_llm:
            prompt_text = load_prompt("info_fetcher_prompt.txt")
            self.prompt = PromptTemplate(
                input_variables=["query"],
                template=prompt_text
            )
            self.llm = ChatOpenAI(model_name=self.model_name, temperature=0)
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
            logger.info(f"🧩 InfoFetcherChain initialized with LLM: {self.model_name}")
        else:
            logger.info("🧩 InfoFetcherChain initialized without LLM, using DB only.")

    @exception_handler
    def run(self, query: str) -> dict:
        """
        Run the InfoFetcher chain
        Steps:
        1. Check MongoDB cache
        2. If not found, optionally call LLM to suggest info
        3. Return structured info
        """
        logger.info(f"[InfoFetcherChain] Fetching info for query: {query}")

        # Step 1: Check MongoDB cache
        cached_info = self.mongo_client.get_info_by_query(query)
        if cached_info:
            logger.info("[InfoFetcherChain] Info found in local DB.")
            return {"status": "available", "info": cached_info}

        # Step 2: Optionally call LLM for suggested info
        if self.use_llm:
            logger.info("[InfoFetcherChain] Info not found in DB. Generating suggestion with LLM.")
            suggested_info = self.chain.run(query=query)
            # Optionally store in DB for caching
            self.mongo_client.save_info(query, suggested_info)
            return {"status": "suggested", "info": suggested_info}

        # Step 3: Info not available
        logger.info("[InfoFetcherChain] Info not available.")
        return {"status": "not_available", "info": None}

