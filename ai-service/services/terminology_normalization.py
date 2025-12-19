# ai-service/services/terminology_normalization.py

import re
import unicodedata
from typing import Optional

# -----------------------
# Shared utilities
# -----------------------

ROMAN_NUMERAL_MAP = {
    "i": "1",
    "ii": "2",
    "iii": "3",
    "iv": "4",
    "v": "5",
}

DOSAGE_PATTERN = re.compile(r"\b\d+\s*(mg|ml|mcg|g|iu|units|%)\b")


def _shared_normalize(text: str) -> str:
    """
    Shared, domain-agnostic normalization.
    Safe for all clinical terms.
    """
    if not text:
        return ""

    # Unicode normalization (smart quotes, accents)
    text = unicodedata.normalize("NFKD", text)

    # Lowercase
    text = text.lower()

    # Remove parentheticals: (adult), (left), (%)
    text = re.sub(r"\([^)]*\)", "", text)

    # Normalize separators
    text = re.sub(r"[-_/]", " ", text)

    # Remove remaining punctuation
    text = re.sub(r"[^a-z0-9\s]", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def _normalize_roman_numerals(text: str) -> str:
    for roman, arabic in ROMAN_NUMERAL_MAP.items():
        text = re.sub(rf"\b{roman}\b", arabic, text)
    return text


def _remove_dosage(text: str) -> str:
    return DOSAGE_PATTERN.sub("", text)


# -----------------------
# Domain-specific entry points
# -----------------------

def normalize_medication_term(text: Optional[str]) -> str:
    """
    Normalize medication names for RxNorm lookup.

    Examples:
    - "Metformin 500mg PO BID" → "metformin"
    - "Lisinopril-10 mg" → "lisinopril"
    """
    if not text:
        return ""

    text = _shared_normalize(text)

    # Medication-specific rules
    text = _remove_dosage(text)

    return text.strip()


def normalize_condition_term(text: Optional[str]) -> str:
    """
    Normalize condition names for SNOMED / ICD lookup.

    Examples:
    - "Type-II diabetes (adult)" → "type 2 diabetes"
    - "Stage III cancer" → "stage 3 cancer"
    """
    if not text:
        return ""

    text = _shared_normalize(text)

    # Condition-specific rules
    text = _normalize_roman_numerals(text)

    return text.strip()


def normalize_lab_term(text: Optional[str]) -> str:
    """
    Normalize lab test names for LOINC lookup.

    Examples:
    - "HbA1c (%)" → "hba1c"
    - "Serum glucose" → "serum glucose"
    """
    if not text:
        return ""

    # Labs get ONLY shared normalization
    # No dosage stripping
    # No roman numeral replacement
    return _shared_normalize(text)
