"""
Multilingual dataset for Hindi and Marathi RTI benchmarking.
"""
from evaluation.datasets.versioning.dataset_manifest import DatasetManifest, BenchmarkQuery

HINDI_QUERIES = [
    BenchmarkQuery(
        id="q_hi_001",
        query="वित्तीय वर्ष 2023-24 में प्रधानमंत्री आवास योजना के तहत ग्रामीण महाराष्ट्र में कितने घर बनाए गए?",
        expected_department="Ministry of Rural Development",
        expected_facts=["2023-24", "प्रधानमंत्री आवास योजना", "महाराष्ट्र", "घर बनाए गए"],
        expected_hallucination=False
    ),
    BenchmarkQuery(
        id="q_hi_002",
        query="क्या मुझे 2024 के लिए राष्ट्रीय राजमार्ग 48 की मरम्मत के लिए आवंटित बजट का विवरण मिल सकता है?",
        expected_department="Ministry of Road Transport and Highways",
        expected_facts=["2024", "राष्ट्रीय राजमार्ग 48", "मरम्मत", "बजट"],
        expected_hallucination=False
    )
]

MARATHI_QUERIES = [
    BenchmarkQuery(
        id="q_mr_001",
        query="पुणे जिल्ह्यातील रस्ते बांधणीसाठी २०२३-२४ या आर्थिक वर्षात मंजूर झालेल्या निधीची माहिती द्या.",
        expected_department="Ministry of Road Transport and Highways",
        expected_facts=["पुणे", "रस्ते बांधणी", "२०२३-२४", "मंजूर निधी"],
        expected_hallucination=False
    ),
    BenchmarkQuery(
        id="q_mr_002",
        query="सार्वजनिक आरोग्य विभागाकडून ग्रामीण रुग्णालयांना मिळालेल्या अनुदानाचा तपशील द्या.",
        expected_department="Department of Health and Family Welfare",
        expected_facts=["आरोग्य विभाग", "ग्रामीण रुग्णालय", "अनुदान"],
        expected_hallucination=False
    )
]

def get_multilingual_datasets():
    return {
        "hi": DatasetManifest(
            dataset_name="hindi_rti_queries",
            version="1.0.0",
            description="High quality Hindi queries.",
            language="hi",
            queries=HINDI_QUERIES
        ),
        "mr": DatasetManifest(
            dataset_name="marathi_rti_queries",
            version="1.0.0",
            description="High quality Marathi queries.",
            language="mr",
            queries=MARATHI_QUERIES
        )
    }
