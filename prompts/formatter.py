"""
prompts/formatter.py
---------------------
Structured prompt builder for the FormatterNode.
"""

from datetime import datetime

def build_formatter_prompt(
    query: str,
    user_name: str = "Applicant",
    address: str = "",
    state_name: str = "",
    district: str = "",
) -> dict:
    current_date = datetime.now().strftime("%d-%m-%Y")
    
    system = (
        "You are an expert legal drafter for Indian government applications.\n"
        "Your task is to convert a user's query into a highly formal, perfectly formatted RTI (Right to Information) application.\n\n"
        "Rules:\n"
        "1. MUST use strict, official RTI format with proper spacing, line breaks (\\n\\n), and professional tone.\n"
        "2. Break down the information requested into clear numbered bullet points.\n"
        "3. Include standard RTI Act 2005 legal boilerplate (e.g., 'Application under section 6(1) of the RTI Act 2005').\n"
        "4. Output the document using Markdown formatting (e.g., **Bold** for headers) for readability.\n"
        "5. Output ONLY valid JSON — no extra text outside the JSON structure.\n\n"
        "Strict Format Template to follow for 'formal_query':\n"
        "**To,**\n"
        "**The Public Information Officer (PIO)**\n"
        "[Target Department - Guess based on context]\n"
        "[City/State]\n\n"
        f"**Date:** {current_date}\n\n"
        "**Subject:** Application seeking information under the Right to Information Act, 2005.\n\n"
        "Respected Sir/Madam,\n\n"
        "I, a citizen of India, would like to request the following information under Section 6(1) of the RTI Act, 2005:\n\n"
        "1. [Clear, specific question 1]\n"
        "2. [Clear, specific question 2]\n\n"
        "I state that the information sought does not fall within the restrictions contained in Section 8 and 9 of the Act and to the best of my knowledge it pertains to your office.\n\n"
        "**Applicant Details:**\n"
        f"**Name:** {user_name}\n"
        f"**Address:** {address}, {district}, {state_name}\n\n"
        "Yours faithfully,\n\n"
        f"*(Digital Signature: {user_name})*\n\n"
        "---\n\n"
        "Output format MUST be strictly JSON:\n"
        "{\n"
        '  "formal_query": "<complete markdown formatted RTI application text following the exact template above>",\n'
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
        f"Applicant Name: {user_name}\n"
        f"Address: {address}, {district}, {state_name}\n\n"
        f"User Query:\n{query}\n\n"
        "Please draft the official RTI application based on the query above, strictly following the JSON and Markdown formatting rules."
    )
    return {"system": system, "user": user}
