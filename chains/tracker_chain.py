# chains/tracker_chain.py

"""
Tracker Chain
-------------
Responsible for managing the RTI tracking workflow.
This chain queries the tracking agent, handles errors, and provides structured responses.
"""

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from agents.tracker_agent import TrackerAgent
from utils.logger import get_logger
from utils.exception_handler import safe_execute

logger = get_logger(__name__)

class TrackerChain:
    """Chain to orchestrate the RTI tracking process."""

    def __init__(self):
        try:
            self.agent = TrackerAgent()
            self.template = PromptTemplate(
                input_variables=["rti_id", "user_query"],
                template=(
                    "You are an RTI Tracking assistant. Given the RTI ID: {rti_id}, "
                    "and user query: '{user_query}', check the database for the RTI request status. "
                    "Provide one of the following:\n"
                    " - Current RTI status\n"
                    " - Expected response date\n"
                    " - Department details\n"
                    " - Any missing tracking info\n"
                    "If information is incomplete, guide the user on next steps clearly."
                ),
            )
            self.chain = LLMChain(llm=self.agent.llm, prompt=self.template)
        except Exception as e:
            logger.error(f"Failed to initialize TrackerChain: {e}")
            raise

    @safe_execute
    def run(self, rti_id: str, user_query: str) -> dict:
        """
        Executes the tracking process for a given RTI ID.
        Returns structured response from the tracker agent.
        """
        logger.info(f"Tracking RTI ID: {rti_id} | Query: {user_query}")

        response = self.chain.invoke({
            "rti_id": rti_id,
            "user_query": user_query
        })

        structured_response = {
            "rti_id": rti_id,
            "query": user_query,
            "result": response.get("text", "No response generated"),
            "status": "success"
        }

        logger.info(f"TrackerChain output: {structured_response}")
        return structured_response
