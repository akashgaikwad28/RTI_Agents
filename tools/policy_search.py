"""
tools/policy_search.py
-----------------------
Searches policy documents relevant to the RTI query.
Returns policy excerpts for RAG context injection.
"""

from observability.structured_logger import get_logger

logger = get_logger(__name__)

_POLICY_KB: dict[str, str] = {
    "rti act": "RTI Act 2005 Section 6: Any person who desires to obtain information shall make a request in writing to the Public Information Officer. Section 7: The PIO shall reply within 30 days.",
    "public information officer": "Every public authority shall designate as many officers as Central Public Information Officers or State Public Information Officers as may be necessary.",
    "appeal": "Under RTI Act 2005, an applicant can file a first appeal within 30 days. Second appeal can be filed with CIC/SIC within 90 days.",
    "fee": "RTI application fee is Rs. 10 for Central Government departments. No fee for BPL applicants.",
    "exemption": "RTI Act Section 8 lists exemptions: national security, cabinet papers, personal information, trade secrets, etc.",
}


async def search_policies(query: str, department: str = "") -> list[str]:
    """Search policy knowledge base for relevant RTI laws and regulations."""
    results = []
    query_lower = query.lower()

    for keyword, policy_text in _POLICY_KB.items():
        if keyword in query_lower or any(word in query_lower for word in keyword.split()):
            results.append(policy_text)

    # Always include basic RTI Act info
    if not results:
        results.append(_POLICY_KB["rti act"])

    logger.info(f"[PolicySearch] Found {len(results)} policy references")
    return results[:2]
