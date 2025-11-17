from typing import Dict, Any

from models.pipeline_models import PipelineRequest, PipelineResponse
from models.extract_models import ExtractResponse
from models.fhir_models import FhirRequest, FhirResponse

from services.summarizer_service import summarize
from services.extractor_service import extract_entities
from services.fhir_service import generate_fhir


def run_pipeline(payload: PipelineRequest) -> PipelineResponse:
    """
    Full text → entities → FHIR (+ summary) pipeline.
    """
    
    summary_result: Dict[str, Any] = summarize(payload.text)
    summary_text = summary_result.get("summary")
    
    entities_dict: Dict[str, Any] = extract_entities(payload.text)
    entities = ExtractResponse(**entities_dict)
    
    fhir_request = FhirRequest(**entities.model_dump())
    
    fhir_bundle_dict: Dict[str, Any] = generate_fhir(fhir_request)
    fhir_bundle = FhirResponse(**fhir_bundle_dict)
    
    return PipelineResponse(
        summary=summary_text,
        entities=entities,
        fhir=fhir_bundle,
    )