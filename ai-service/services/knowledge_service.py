import csv
import os
from typing import Dict, Optional, List

from services.terminology_normalization import (
    normalize_condition_term,
    normalize_medication_term,
    normalize_lab_term,
)

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


# ---------------------------------------------------------
# Load CSV into memory (simple & fast for demo)
# ---------------------------------------------------------

def load_csv(filename: str) -> List[Dict[str, str]]:
    path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


# ---------------------------------------------------------
# Load datasets at startup
# ---------------------------------------------------------

SNOMED_DATA = load_csv("snomed.csv")
ICD10_DATA = load_csv("icd10.csv")
RXNORM_DATA = load_csv("rxnorm.csv")
LOINC_DATA = load_csv("loinc.csv")


# =========================================================
# SNOMED LOOKUP (conditions)
# =========================================================

def lookup_snomed(term: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Resolve a condition term to SNOMED CT using deterministic normalization.

    - Original input text is NEVER modified
    - Normalization is applied only for lookup comparison
    """

    if not term:
        return None

    normalized_input = normalize_condition_term(term)

    for row in SNOMED_DATA:
        # Match primary term
        if normalize_condition_term(row["term"]) == normalized_input:
            return {
                "system": "http://snomed.info/sct",
                "code": row["code"],
                "display": row["preferred"],
            }

        # Match synonyms
        synonyms = row.get("synonyms")
        if synonyms:
            for s in synonyms.split(","):
                if normalize_condition_term(s) == normalized_input:
                    return {
                        "system": "http://snomed.info/sct",
                        "code": row["code"],
                        "display": row["preferred"],
                    }

    return None


# =========================================================
# ICD-10 LOOKUP (conditions)
# =========================================================

def lookup_icd10(term: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Resolve a condition term to ICD-10.

    Used primarily for reporting/billing support.
    """

    if not term:
        return None

    normalized_input = normalize_condition_term(term)

    for row in ICD10_DATA:
        if normalize_condition_term(row["term"]) == normalized_input:
            return {
                "system": "http://hl7.org/fhir/sid/icd-10-cm",
                "code": row["code"],
                "display": row["term"],
            }

    return None


# =========================================================
# RxNorm LOOKUP (medications)
# =========================================================

def lookup_rxnorm(name: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Resolve a medication name to RxNorm.

    - Strips dosage and administration noise
    - Matches against canonical drug names and synonyms
    """

    if not name:
        return None

    normalized_input = normalize_medication_term(name)

    for row in RXNORM_DATA:
        # Match primary name
        if normalize_medication_term(row["name"]) == normalized_input:
            return {
                "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                "code": row["rxnorm"],
                "display": row["name"],
            }

        # Match synonyms
        synonyms = row.get("synonyms")
        if synonyms:
            for s in synonyms.split(","):
                if normalize_medication_term(s) == normalized_input:
                    return {
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "code": row["rxnorm"],
                        "display": row["name"],
                    }

    return None


# =========================================================
# LOINC LOOKUP (labs)
# =========================================================

def lookup_loinc(test: Optional[str]) -> Optional[Dict[str, str]]:
    """
    Resolve a lab test name to LOINC.

    - Conservative normalization
    - Preserves lab semantics (no dosage stripping)
    """

    if not test:
        return None

    normalized_input = normalize_lab_term(test)

    for row in LOINC_DATA:
        if normalize_lab_term(row["test"]) == normalized_input:
            return {
                "system": "http://loinc.org",
                "code": row["code"],
                "display": row["component"],
            }

    return None
