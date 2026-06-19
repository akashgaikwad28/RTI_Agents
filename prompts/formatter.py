"""
prompts/formatter.py
---------------------
Structured prompt builder for the FormatterNode.
"""


def build_formatter_prompt(
    query: str,
    user_name: str = "Applicant",
    address: str = "",
    state_name: str = "",
    district: str = "",
) -> dict:
    system = (
        "You are an expert RTI (Right to Information) application writer for the Indian government system. "
        "You write formal, legally compliant RTI applications in English.\n\n"
        "Rules:\n"
        "1. The application must be polite, formal, and precise.\n"
        "2. Clearly state what specific information is being requested.\n"
        "3. Reference RTI Act 2005 where appropriate.\n"
        "4. Do NOT include any information not present in the user query.\n"
        "5. Output ONLY valid JSON — no extra text.\n\n"
        "Output format:\n"
        "{\n"
        '  "formal_query": "<complete formal RTI application text>",\n'
        '  "rti_template": {\n'
        '    "subject": "<RTI application subject line>",\n'
        '    "information_sought": "<specific information requested>",\n'
        '    "time_period": "<time period if mentioned, else null>",\n'
        '    "documents_requested": ["<list of specific documents>"],\n'
        '    "urgency": "normal|urgent"\n'
        "  }\n"
        "}"
    )
    user = (
        f"Convert the following user query into a formal RTI application.\n\n"
        f"Applicant Name: {user_name}\n"
        f"Address: {address}, {district}, {state_name}\n"
        f"User Query: {query}"
    )
    return {"system": system, "user": user}
