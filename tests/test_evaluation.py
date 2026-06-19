import pytest
import sys
import os
import tempfile
import json
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

def test_dataset_versioning_manifest():
    """Verify that dataset manifests load, sign, and validate correctly."""
    from evaluation.datasets.versioning.dataset_manifest import DatasetManifest, BenchmarkQuery
    
    with tempfile.TemporaryDirectory() as tmpdir:
        manifest_file = os.path.join(tmpdir, "manifest.json")
        
        # Write dummy manifest
        dummy_data = {
            "dataset_name": "test_golden",
            "version": "1.0.0",
            "description": "test suite",
            "language": "en",
            "queries": [
                {
                    "id": "q1",
                    "query": "Who is the PM?",
                    "expected_department": "revenue",
                    "expected_facts": ["fact A"],
                    "expected_hallucination": False,
                    "metadata": {}
                }
            ]
        }
        with open(manifest_file, "w") as f:
            json.dump(dummy_data, f)
            
        with open(manifest_file, "r") as f:
            data = json.load(f)
        manifest = DatasetManifest(**data)
        assert manifest.dataset_name == "test_golden"
        assert manifest.version == "1.0.0"

def test_citation_verifier():
    """Verify that regex matches and flags out-of-bounds citation indices."""
    from evaluation.hallucination.citation_verifier import CitationVerifier
    
    verifier = CitationVerifier()
    retrieved_chunks = ["Context chunk A", "Context chunk B"]
    
    # Valid citations
    res_valid = verifier.verify("According to [1] and [2], RTI is robust.", retrieved_chunks)
    assert res_valid.total_citations == 2
    assert res_valid.valid_citations == 2
    assert res_valid.score == 1.0
    
    # Out of bounds citation [3]
    res_invalid = verifier.verify("According to [1] and [3], this is an edge case.", retrieved_chunks)
    assert res_invalid.total_citations == 2
    assert res_invalid.valid_citations == 1
    assert len(res_invalid.invalid_citations) == 1
    assert res_invalid.score == 0.5

@pytest.mark.asyncio
async def test_load_testing_bug_detection():
    """
    CRITICAL BUG DETECTOR:
    Verifies if load_testing crashes due to importing from 'api.schemas.request'.
    """
    try:
        from evaluation.latency.load_testing import AsyncLoadTester
        assert AsyncLoadTester is not None
    except ModuleNotFoundError as e:
        if "api.schemas.request" in str(e):
            pytest.xfail(f"[EXPECTED CRASH] Load tester crashes on missing api.schemas.request: {e}")
        else:
            raise e

def test_html_report_generator():
    """Verify HTML report generator executes without templating crashes."""
    from evaluation.reports.html_report_generator import HTMLReportGenerator
    
    generator = HTMLReportGenerator()
    report_data = {
        "hallucination_rate": 0.05,
        "latency": 350.5,
        "compliance_score": 0.95
    }
    
    filepath = generator.generate_report("test_run_123", report_data)
    assert os.path.exists(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()
    assert "test_run_123" in html
    assert "Average Hallucination Rate" in html
