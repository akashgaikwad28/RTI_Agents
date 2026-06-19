"""
tools/department_lookup.py
---------------------------
Returns the canonical list of Indian government departments
for RTI classification. Acts as a constraint for the Classifier.
"""

# Canonical Indian government departments for RTI routing
VALID_DEPARTMENTS = [
    "Ministry of Agriculture & Farmers Welfare",
    "Ministry of Education",
    "Ministry of Health and Family Welfare",
    "Ministry of Housing and Urban Affairs",
    "Ministry of Jal Shakti (Water Resources)",
    "Ministry of Labour and Employment",
    "Ministry of Law and Justice",
    "Ministry of Railways",
    "Ministry of Road Transport and Highways",
    "Ministry of Rural Development",
    "Ministry of Social Justice and Empowerment",
    "Ministry of Women and Child Development",
    "Department of Telecommunications",
    "Department of Revenue",
    "Department of Posts",
    "Department of Financial Services",
    "Central Electricity Authority",
    "Food Corporation of India",
    "Income Tax Department",
    "Municipal Corporation",
    "State Public Works Department",
    "State Electricity Board",
    "State Agriculture Department",
    "State Education Department",
    "State Health Department",
    "State Revenue Department",
    "State Water Supply Department",
    "Gram Panchayat",
    "Unknown Department",
]


def get_valid_departments() -> list[str]:
    """Returns the list of valid RTI target departments."""
    return VALID_DEPARTMENTS


MAP_REGISTRATION_TO_CANONICAL = {
    "agriculture": [
        "Ministry of Agriculture & Farmers Welfare",
        "State Agriculture Department",
    ],
    "road-transport": [
        "Ministry of Road Transport and Highways",
        "State Public Works Department",
    ],
    "education": [
        "Ministry of Education",
        "State Education Department",
    ],
    "health": [
        "Ministry of Health and Family Welfare",
        "State Health Department",
    ],
    "municipal": [
        "Municipal Corporation",
        "Gram Panchayat",
        "Ministry of Housing and Urban Affairs",
    ],
}


def get_canonical_departments_for_registration(reg_dept: str) -> list[str]:
    """
    Returns a list of canonical department names associated with a simplified registration department name.
    """
    if not reg_dept:
        return []
    
    reg_dept_lower = reg_dept.lower().strip()
    
    # If the user registered directly with a canonical name, return it
    for canonical in VALID_DEPARTMENTS:
        if canonical.lower() == reg_dept_lower:
            return [canonical]
            
    # Otherwise, map the simplified term
    return MAP_REGISTRATION_TO_CANONICAL.get(reg_dept_lower, [reg_dept])

