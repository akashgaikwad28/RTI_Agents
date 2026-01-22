# app.py - auto-generated
"""
app.py
------
Main orchestration file for RTI_Agent
- Connects Formatter, Classifier, InfoFetcher, Tracker agents
- Handles end-to-end RTI workflow
- Uses GraphManager for scalable modular workflow
"""

from agents.base.graph_manager import GraphManager
from agents.formatter_agent import FormatterAgent
from agents.classifier_agent import ClassifierAgent
from agents.info_fetcher_agent import InfoFetcherAgent
from agents.tracker_agent import TrackerAgent
from utils.logger import logger
from utils.exception_handler import exception_handler
from schemas.rti_query_schema import RTIRequestSchema

# Initialize agents
formatter_agent = FormatterAgent()
classifier_agent = ClassifierAgent()
info_fetcher_agent = InfoFetcherAgent()
tracker_agent = TrackerAgent()

# Initialize GraphManager
graph_manager = GraphManager()
graph_manager.register_agent("formatter", formatter_agent)
graph_manager.register_agent("classifier", classifier_agent)
graph_manager.register_agent("info_fetcher", info_fetcher_agent)
graph_manager.register_agent("tracker", tracker_agent)

@exception_handler
def submit_rti_request(user_input: dict):
    """
    Main RTI workflow:
    1. Validate input
    2. Format query
    3. Classify department
    4. Check info availability
    5. Track request
    """
    # Step 1: Validate input using Pydantic
    validated_input = RTIRequestSchema(**user_input)
    context = validated_input.dict()
    logger.info("[app] User input validated.")

    # Step 2: Format query
    formatted_result = graph_manager.run_agent("formatter", context)
    context.update(formatted_result)
    logger.info(f"[app] Query formatted: {formatted_result.get('formal_query')}")

    # Step 3: Classify department
    classification_result = graph_manager.run_agent("classifier", context)
    context.update(classification_result)
    logger.info(f"[app] Department classified: {classification_result.get('department')}")

    # Step 4: Check if info already exists
    info_result = graph_manager.run_agent("info_fetcher", context)
    context.update(info_result)

    if info_result.get("status") == "available":
        logger.info("[app] Info available on portal. Returning result to user.")
        return {
            "status": "info_available",
            "info": info_result.get("info")
        }

    # Step 5: Info not available, create tracking ID and send RTI
    tracking_id = graph_manager.run_agent("tracker", {
        "user_data": context.get("user_data"),
        "formatted_query": context.get("formal_query")
    })
    logger.info(f"[app] RTI submitted with tracking ID: {tracking_id}")

    return {
        "status": "submitted",
        "tracking_id": tracking_id
    }

# Example usage
if __name__ == "__main__":
    sample_user_input = {
    "name": "Akash Gaikwad",
    "gender": "male",
    "address": "Pune, Maharashtra",
    "pincode": "411001",
    "country": "India",
    "state": "Maharashtra",
    "district": "Pune",
    "tehsil": "Haveli",
    "village": "N/A",
    "location_type": "urban",
    "education_status": "literate",
    "phone_number": "9876543210",
    "email": "akash@example.com",
    "query_text": "I want details about local agriculture schemes"
}

    result = submit_rti_request(sample_user_input)
    print(result)
