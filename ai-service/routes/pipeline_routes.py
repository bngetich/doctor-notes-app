from fastapi import APIRouter

from models.pipeline_models import PipelineRequest, PipelineResponse
from services.pipeline_service import run_pipeline

router = APIRouter(tags=["Pipeline"])

@router.post(
    "/pipeline",
    response_model=PipelineResponse,
    summary="Run full clinical pipeline"
)
def pipeline_route(request: PipelineRequest):
    """
    Run the full clinical pipeline:
    - Generate a summary
    - Extract structured entities
    - Convert entities into a FHIR Bundle
    """
    return run_pipeline(request)