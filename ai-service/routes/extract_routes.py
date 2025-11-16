from fastapi import APIRouter
from models.note_models import NoteRequest
from models.extract_models import ExtractResponse
from services.extractor_service import extract_entities


router = APIRouter()


@router.post(
    "/extract",
    response_model=ExtractResponse,
    summary="Extract structured entities"
)
def extract(request: NoteRequest):
    """
    Extract conditions, symptoms, medications, and procedures from raw clinical text.
    """
    return extract_entities(request.text)