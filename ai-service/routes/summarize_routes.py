from fastapi import APIRouter
from models.note_models import NoteRequest, NoteResponse
from services.summarizer_service import summarize


router = APIRouter()

@router.post(
    "/summarize", 
    response_model=NoteResponse,
    summary="Summarize clinical text"
)
def analyze_text(request: NoteRequest):
    """
    Generate a clinical summary from unstructured clinical text.
    """
    return summarize(request.text)   