"""
tools/search_gov_portal.py
---------------------------
Simulated government portal search tool.
In production, replace with real RTI portal API/scraping.
"""

from observability.structured_logger import get_logger

logger = get_logger(__name__)

# Simulated government knowledge base
_PORTAL_KNOWLEDGE: dict[str, list[str]] = {
    "road": [
        "Under RTI Act 2005, PWD road construction budgets must be disclosed within 30 days.",
        "Road construction tenders are publicly available at the state PWD portal.",
    ],
    "water": [
        "Water supply scheme information is maintained by the Jal Jeevan Mission.",
        "Monthly water quality reports are mandatorily disclosed by water boards.",
    ],
    "school": [
        "School enrollment data is published annually by UDISE+ portal.",
        "Mid-day meal scheme details are available at state education departments.",
    ],
    "agriculture": [
        "PM-KISAN scheme beneficiary list is publicly available at pmkisan.gov.in",
        "Crop insurance claims under PMFBY can be tracked online.",
    ],
    "electricity": [
        "Electricity tariff orders are publicly available at SERC websites.",
        "Power outage schedules are mandatorily published by state DISCOMs.",
    ],
    "health": [
        "AYUSHMAN Bharat beneficiary data is available at pmjay.gov.in.",
        "Government hospital bed availability is tracked on the national health portal.",
    ],
}


async def search_gov_portal(query: str, department: str = "") -> list[str]:
    """
    Search simulated government portal for relevant information.

    Args:
        query: RTI query text
        department: Target department (used for context)

    Returns:
        List of relevant portal information strings
    """
    results = []
    query_lower = query.lower()

    for keyword, info_list in _PORTAL_KNOWLEDGE.items():
        if keyword in query_lower or keyword in department.lower():
            results.extend(info_list)

    if results:
        logger.info(f"[GovPortalSearch] Found {len(results)} results for query")
    else:
        logger.info("[GovPortalSearch] No portal results found")

    return results[:3]  # Return max 3 results
