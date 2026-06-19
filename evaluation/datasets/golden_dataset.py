"""
Golden dataset containing high-quality, verified RTI queries.
"""
from evaluation.datasets.versioning.dataset_manifest import DatasetManifest, BenchmarkQuery

GOLDEN_QUERIES = [
    BenchmarkQuery(
        id="q_road_001",
        query="Provide the total budget allocated and spent for the construction of the Pune-Mumbai Expressway during the financial year 2023-24.",
        expected_department="Ministry of Road Transport and Highways",
        expected_facts=["budget allocated", "spent", "Pune-Mumbai Expressway", "2023-24"],
        expected_hallucination=False
    ),
    BenchmarkQuery(
        id="q_muni_002",
        query="Requesting the list of approved municipal projects for solid waste management in Bangalore urban district for 2024.",
        expected_department="Ministry of Housing and Urban Affairs",
        expected_facts=["approved municipal projects", "solid waste management", "Bangalore urban", "2024"],
        expected_hallucination=False
    ),
    BenchmarkQuery(
        id="q_edu_003",
        query="What is the total education grant provided to primary schools in rural Maharashtra under the Sarva Shiksha Abhiyan?",
        expected_department="Department of School Education and Literacy",
        expected_facts=["education grant", "primary schools", "rural Maharashtra", "Sarva Shiksha Abhiyan"],
        expected_hallucination=False
    ),
    BenchmarkQuery(
        id="q_agri_004",
        query="Details of PM-KISAN agriculture subsidies disbursed in Punjab during the Kharif season of 2023.",
        expected_department="Department of Agriculture and Farmers Welfare",
        expected_facts=["PM-KISAN", "subsidies disbursed", "Punjab", "Kharif season", "2023"],
        expected_hallucination=False
    ),
    BenchmarkQuery(
        id="q_health_005",
        query="Provide the allocation of healthcare budget for building new AIIMS facilities in southern states.",
        expected_department="Department of Health and Family Welfare",
        expected_facts=["healthcare budget", "AIIMS facilities", "southern states"],
        expected_hallucination=False
    )
]

def get_golden_dataset() -> DatasetManifest:
    return DatasetManifest(
        dataset_name="golden_rti_queries",
        version="1.0.0",
        description="High quality English queries covering core governance areas.",
        language="en",
        queries=GOLDEN_QUERIES
    )
