# tests/test_condition_coding.py

from unittest.mock import patch

from services.fhir_service import build_condition_code
from services.knowledge_service import lookup_snomed


def extract_codes(code_obj):
    """Helper: return list of codes from a CodeableConcept."""
    return [c["code"] for c in code_obj.get("coding", [])]


def test_rag_invalid_code_falls_back_to_csv():
    """
    GIVEN a RAG result with an incorrect SNOMED code
    WHEN build_condition_code is called
    THEN the RAG code is rejected
    AND the CSV-backed SNOMED code is used instead
    """
    term = "type 2 diabetes"

    csv_snomed = lookup_snomed(term)
    assert csv_snomed is not None, "Test requires SNOMED CSV entry to exist"

    fake_rag_result = [{
        "system": "http://snomed.info/sct",
        "code": "99999999",  # invalid code
        "display": "type 2 diabetes"
    }]

    with patch("services.fhir_service.rag_lookup", return_value=fake_rag_result):
        code_obj = build_condition_code(term)

    codes = extract_codes(code_obj)

    assert "99999999" not in codes, "Invalid RAG code must be rejected"
    assert csv_snomed["code"] in codes, "CSV SNOMED must be used as fallback"


def test_rag_valid_code_is_accepted_without_csv_fallback():
    """
    GIVEN a RAG result with a valid SNOMED code
    WHEN build_condition_code is called
    THEN the RAG code is accepted
    AND no CSV fallback is required
    """
    term = "type 2 diabetes"

    valid_rag_result = [{
        "system": "http://snomed.info/sct",
        "code": "44054006",
        "display": "type 2 diabetes mellitus"
    }]

    with patch("services.fhir_service.rag_lookup", return_value=valid_rag_result):
        code_obj = build_condition_code(term)

    codes = extract_codes(code_obj)

    assert "44054006" in codes, "Valid RAG code must be preserved"
