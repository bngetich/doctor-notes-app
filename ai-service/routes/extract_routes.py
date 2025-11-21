# ai-service/routes/extract_routes.py

from fastapi import APIRouter
from models.extract_models import ExtractRequest, ExtractResponse
from services.extractor_service import extract_entities

router = APIRouter(tags=["Extraction"])

@router.post(
    "/extract",
    response_model=ExtractResponse,
    summary="Extract structured entities from clinical text"
)
def extract_route(request: ExtractRequest):
    """
    Extract patient info, problems, medications, vitals, labs,
    imaging, social/family history, assessment, and plan
    from raw clinical text.
    """
    return extract_entities(request.text)
