# ai-service/services/pipeline_service.py

from services.summarizer_service import summarize
from services.extractor_service import extract_entities
from services.schema_normalization import normalize_entities
from services.fhir_service import generate_fhir_resource
from services.validation_service import validate_entities

from models.extract_models import ExtractResponse
from models.pipeline_models import PipelineRequest, PipelineResponse
from models.fhir_models import FhirBundleResponse


def run_pipeline(payload: PipelineRequest) -> PipelineResponse:
    """
    Full clinical text → summary → extraction → normalization → validation → FHIR.

        1. Summarize text
        2. Extract raw entities using LLM
        3. Schema normalization
        4. Structural validation
        5. Convert to ExtractResponse
        6. Generate FHIR Bundle (includes terminology resolution)
    """

    text = payload.text

    # --------------------------------
    # 1. Summarization
    # --------------------------------
    summary_data = summarize(text)

    # --------------------------------
    # 2. Extraction
    # --------------------------------
    raw_entities = extract_entities(text)

    # --------------------------------
    # 3. Schema normalization
    # --------------------------------
    clean_entities = normalize_entities(raw_entities)

    # --------------------------------
    # 4. Validation (text-only, pre-FHIR)
    # --------------------------------
    validate_entities(clean_entities)

    # --------------------------------
    # 5. Convert dict → ExtractResponse
    # --------------------------------
    entities_model = ExtractResponse(**clean_entities)

    # --------------------------------
    # 6. Generate FHIR Bundle
    # --------------------------------
    fhir_bundle = generate_fhir_resource(entities_model)
    fhir_response = FhirBundleResponse(**fhir_bundle)

    return PipelineResponse(
        summary=summary_data["summary"],
        entities=entities_model,
        fhir=fhir_response,
    )
