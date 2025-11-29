# ai-service/services/pipeline_service.py

from typing import Dict, Any

from services.summarizer_service import summarize
from services.extractor_service import extract_entities
from services.normalization_service import normalize_entities
from services.fhir_service import generate_fhir_resource
from models.extract_models import ExtractResponse


def run_pipeline(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Full clinical text → summary → extraction → normalization → FHIR pipeline.

        1. Summarize text
        2. Extract raw entities using LLM
        3. Normalize entities
        4. Convert normalized entities into ExtractResponse (Pydantic)
        5. Generate FHIR Bundle
    """

    text = payload["text"]

    # --------------------------------
    # 1. Summarization
    # --------------------------------
    summary_data = summarize(text)

    # --------------------------------
    # 2. Extraction
    # --------------------------------
    raw_entities = extract_entities(text)

    # --------------------------------
    # 3. Normalization
    # --------------------------------
    clean_entities = normalize_entities(raw_entities)

    # --------------------------------
    # 4. Convert dict → ExtractResponse model
    # --------------------------------
    entities_model = ExtractResponse(**clean_entities)

    # --------------------------------
    # 5. Generate FHIR Bundle
    # --------------------------------
    fhir_bundle = generate_fhir_resource(entities_model)

    # --------------------------------
    # Final output
    # --------------------------------
    return {
        "summary": summary_data["summary"],
        "entities": clean_entities,
        "fhir": fhir_bundle,
    }
