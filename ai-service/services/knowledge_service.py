import csv
import os
from typing import Dict, Optional, List
from services.terminology_normalization import normalize_clinical_term


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
# Load all datasets at service startup
# ---------------------------------------------------------
SNOMED_DATA = load_csv("snomed.csv")
ICD10_DATA = load_csv("icd10.csv")
RXNORM_DATA = load_csv("rxnorm.csv")
LOINC_DATA = load_csv("loinc.csv")


# =====================================================================
# SNOMED LOOKUP
# =====================================================================
def lookup_snomed(term: str) -> Optional[Dict[str, str]]:
    """
    Return SNOMED coding object for a condition.
    Example return:
    {
        "system": "http://snomed.info/sct",
        "code": "44054006",
        "display": "Type 2 diabetes mellitus"
     }
    """
    t = normalize_clinical_term(term)

    for row in SNOMED_DATA:
        if normalize_clinical_term(row["term"]) == t:
            return {
                "system": "http://snomed.info/sct",
                "code": row["code"],
                "display": row["preferred"],
            }

        # match synonyms
        if row.get("synonyms"):
            for s in row["synonyms"].split(","):
                if normalize_clinical_term(s) == t:
                    return {
                        "system": "http://snomed.info/sct",
                        "code": row["code"],
                        "display": row["preferred"],
                    }
                
    return None

# =====================================================================
# ICD-10 LOOKUP
# =====================================================================
def lookup_icd10(term: str) -> Optional[Dict[str, str]]:
    t = normalize_clinical_term(term)

    for row in ICD10_DATA:
        if normalize_clinical_term(row["term"]) == t:
            return {
                "system": "http://hl7.org/fhir/sid/icd-10-cm",
                "code": row["code"],
                "display": row["term"]
            }

    return None


# =====================================================================
# RxNorm LOOKUP (medications)
# =====================================================================
def lookup_rxnorm(name: str) -> Optional[Dict[str, str]]:
    n = normalize_clinical_term(name)

    for row in RXNORM_DATA:
        if normalize_clinical_term(row["name"]) == n:
            return {
                "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                "code": row["rxnorm"],
                "display": row["name"]
            }

        if row.get("synonyms"):
            for s in row["synonyms"].split(","):
                if normalize_clinical_term(s) == n:
                    return {
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "code": row["rxnorm"],
                        "display": row["name"]
                    }

    return None


# =====================================================================
# LOINC LOOKUP (labs)
# =====================================================================
def lookup_loinc(test: str) -> Optional[Dict[str, str]]:
    t = normalize_clinical_term(test)

    for row in LOINC_DATA:
        if normalize_clinical_term(row["test"]) == t:
            return {
                "system": "http://loinc.org",
                "code": row["code"],
                "display": row["component"]
            }

    return None
