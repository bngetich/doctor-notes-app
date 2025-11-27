# ai-service/services/pipeline_service.py

from typing import Dict, Any

from services.summarizer_service import summarize
from services.extractor_service import extract_entities
from services.normalization_service import normalize_entities
from services.fhir_service import generate_fhir_resource


def run_pipeline(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full clinical text → summary → extraction → normalization → FHIR pipeline.

    This is the orchestrator that performs the entire workflow:

        1. Summarize unstructured text using the LLM
        2. Extract structured entities using the LLM
        3. Normalize/clean the extracted entities (fix formatting)
        4. Generate a full FHIR Bundle from the normalized data

    Returns a combined dict with all outputs.
    """

    text = payload["text"]

    # -----------------------------
    #   1. Summarization (LLM)
    # -----------------------------
    summary_data = summarize(text)
    # summary_data = { "summary": "...", "diagnoses": [...], "symptoms": [...], ... }

    # -----------------------------
    #   2. Extraction (LLM)
    # -----------------------------
    raw_entities = extract_entities(text)
    # raw_entities = messy JSON from LLM

    # -----------------------------
    #   3. Normalization (IMPORTANT)
    # -----------------------------
    clean_entities = normalize_entities(raw_entities)
    # clean_entities = stable, safe, normalized structure

    # -----------------------------
    #   4. FHIR Bundle
    # -----------------------------
    fhir_bundle = generate_fhir_resource(clean_entities)

    # -----------------------------
    #   Final output to requestor
    # -----------------------------
    return {
        "summary": summary_data["summary"],
        "entities": clean_entities,
        "fhir": fhir_bundle,
    }
