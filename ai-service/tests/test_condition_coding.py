# tests/test_condition_coding.py

import pytest
from unittest.mock import patch

from services.fhir_service import build_condition_code
from services.knowledge_service import lookup_snomed, lookup_icd10


"""
Goal:

If rag_lookup returns a candidate whose code DOES NOT match what the CSV
database says, then build_condition_code() must reject that RAG output and
fall back to standard CSV lookup_snomed/lookup_icd10.
"""


def test_rag_invalid_code_falls_back_to_csv():
    term = "type 2 diabetes"

    # Local CSV truth (what knowledge_service actually returns)
    csv_snomed = lookup_snomed(term)
    assert csv_snomed is not None, "CSV SNOMED must exist for the test"

    # WRONG coding returned by RAG (simulating an embedding mistake)
    fake_rag_result = [{
        "system": "http://snomed.info/sct",
        "code": "99999999",                    # WRONG CODE on purpose
        "display": "type 2 diabetes"
    }]

    with patch("services.fhir_service.rag_lookup", return_value=fake_rag_result):
        code_obj = build_condition_code(term)

    # ---- VALIDATION ----
    # The incorrect RAG code must NOT appear
    assert "coding" in code_obj, "build_condition_code() should still output coding"
    
    codes = [c["code"] for c in code_obj["coding"]]

    assert "99999999" not in codes, \
        "RAG's wrong code MUST be rejected and not included in FHIR output."

    # ---- MUST FALL BACK TO CSV ----
    assert csv_snomed["code"] in codes, \
        "CSV SNOMED code MUST be used when RAG is invalid."

    # ICD-10 fallback is also allowed
    # (depends on your CSV having ICD10 entry for the term)
