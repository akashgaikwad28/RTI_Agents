"""Tests for Table extraction logic."""

import pytest
from rag.tables.table_extractor import TableExtractor

@pytest.mark.unit
def test_table_extractor_semantic_sentence():
    sentence = TableExtractor._create_semantic_sentence(
        table_name="Budget 2024",
        row=["Pune", "100 Cr", "Approved"],
        headers=["District", "Budget", "Status"]
    )
    assert "Regarding Budget 2024:" in sentence
    assert "District is Pune" in sentence
    assert "Budget is 100 Cr" in sentence
    assert "Status is Approved" in sentence

@pytest.mark.unit
def test_table_extractor_dummy_integration():
    res = TableExtractor.extract_and_format("dummy.pdf", 1)
    assert res is not None
    assert "table_schema" in res
    assert "column_headers" in res
