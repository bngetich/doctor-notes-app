from unittest.mock import patch

from services.terminology_service import resolve_condition
from services.knowledge_service import lookup_snomed


def extract_codes(result):
    """Helper: extract code values from resolve_condition result."""
    return [c["code"] for c in result.get("coding", [])]


def test_authoritative_lookup_short_circuits_rag():
    """
    GIVEN a condition that exists in the authoritative vocabulary
    WHEN resolve_condition is called
    THEN the authoritative SNOMED code is returned
    AND RAG is never invoked
    """
    term = "type 2 diabetes"

    csv_snomed = lookup_snomed(term)
    assert csv_snomed is not None, "Test requires SNOMED CSV entry to exist"

    with patch("services.terminology_service.rag_lookup") as mock_rag:
        result = resolve_condition(term)

    codes = extract_codes(result)

    assert csv_snomed["code"] in codes
    mock_rag.assert_not_called()


def test_rag_used_only_when_csv_lookup_fails():
    """
    GIVEN a malformed condition that does NOT exist in CSV
    WHEN resolve_condition is called
    THEN RAG is used as a fallback
    AND the verified SNOMED code is returned
    """
    term = "typ 2 diabtes"  # intentionally malformed

    fake_rag_result = [{
        "system": "http://snomed.info/sct",
        "code": "44054006",
        "display": "Type 2 diabetes",
    }]

    with patch(
        "services.terminology_service.rag_lookup",
        return_value=fake_rag_result,
    ):
        result = resolve_condition(term)

    codes = extract_codes(result)

    assert "44054006" in codes


def test_invalid_rag_code_is_rejected():
    """
    GIVEN a malformed condition
    AND RAG returns a coding with an invalid SNOMED code
    WHEN resolve_condition is called
    THEN the invalid RAG code is rejected
    AND the condition remains uncoded
    """
    term = "typ 2 diabtes"

    invalid_rag_result = [{
        "system": "http://snomed.info/sct",
        "code": "99999999",  # invalid SNOMED code
        "display": "Type 2 diabetes mellitus",
    }]

    with patch(
        "services.terminology_service.rag_lookup",
        return_value=invalid_rag_result,
    ):
        result = resolve_condition(term)

    assert "coding" not in result
