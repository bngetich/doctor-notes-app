# ai-service/services/terminology_service.py

from typing import Dict, Any, Optional

from services.knowledge_service import lookup_snomed, lookup_icd10, lookup_rxnorm, lookup_loinc
from services.validation_service import validate_rag_coding_shape
from rag.rag_search import rag_lookup


def verify_coding_against_vocab(
    term: str,
    coding: Dict[str, str],
) -> Optional[Dict[str, str]]:
    """
    Verify a RAG-returned coding against authoritative vocabularies.
    """

    display = coding.get("display") or term

    snomed = lookup_snomed(display)
    if snomed and snomed["code"] == coding["code"]:
        return coding

    icd10 = lookup_icd10(display)
    if icd10 and icd10["code"] == coding["code"]:
        return coding

    return None


def resolve_condition(term: str) -> Dict[str, Any]:
    """
    Resolve a condition term into a CodeableConcept-like dict.
    """

    result: Dict[str, Any] = {"text": term}

    # --------------------------------------------------
    # 1. Deterministic lookup (authoritative)
    # --------------------------------------------------
    snomed = lookup_snomed(term)
    if snomed:
        result["coding"] = [snomed]
        return result

    icd10 = lookup_icd10(term)
    if icd10:
        result["coding"] = [icd10]
        return result

    # --------------------------------------------------
    # 2. RAG fallback (candidate generation)
    # --------------------------------------------------
    for candidate in rag_lookup(term) or []:
        if not validate_rag_coding_shape(candidate):
            continue

        verified = verify_coding_against_vocab(term, candidate)
        if verified:
            result["coding"] = [verified]
            return result

    # --------------------------------------------------
    # 3. Honest uncoded fallback
    # --------------------------------------------------
    return result


def resolve_medication(name: str) -> Optional[Dict[str, str]]:
    """
    Resolve medication name via RxNorm.
    """
    return lookup_rxnorm(name)


def resolve_lab(test: str) -> Optional[Dict[str, str]]:
    """
    Resolve lab test via LOINC.
    """
    return lookup_loinc(test)
