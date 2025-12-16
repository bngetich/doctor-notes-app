# ai-service/services/terminology_normalization.py

import re
import unicodedata

# Small, explicit maps are intentional
ROMAN_NUMERAL_MAP = {
    "i": "1",
    "ii": "2",
    "iii": "3",
    "iv": "4",
    "v": "5",
}

DOSAGE_PATTERN = re.compile(r"\b\d+\s*(mg|ml|mcg|g|iu|units|%)\b")


def normalize_clinical_term(text: str) -> str:
    """
    Deterministically normalize clinical terminology for lookup.

    This function:
    - does NOT infer meaning
    - does NOT assign codes
    - does NOT call RAG
    - does NOT access CSVs

    It exists solely to produce a stable lookup key.
    """
    if not text:
        return ""

    # Unicode normalization (handles smart quotes, accents, etc.)
    text = unicodedata.normalize("NFKD", text)

    # Lowercase
    text = text.lower()

    # Remove parentheticals: (adult), (%), etc.
    text = re.sub(r"\([^)]*\)", "", text)

    # Replace separators with space
    text = re.sub(r"[-_/]", " ", text)

    # Convert roman numerals → arabic (type ii → type 2)
    for roman, arabic in ROMAN_NUMERAL_MAP.items():
        text = re.sub(rf"\b{roman}\b", arabic, text)

    # Remove dosage expressions (500mg, 10 %, etc.)
    text = DOSAGE_PATTERN.sub("", text)

    # Remove remaining non-alphanumeric characters
    text = re.sub(r"[^a-z0-9\s]", "", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text
