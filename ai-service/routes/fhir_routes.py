from fastapi import APIRouter
from models.fhir_models import FhirRequest, FhirResponse
from services.fhir_service import generate_fhir


router = APIRouter()

@router.post(
    "/fhir",
    response_model=FhirResponse,
    summary="Generate FHIR Bundle"
)
def generate_fhir_resource(request: FhirRequest):
    """
    Take structured clinical entities and build a FHIR Bundle.
    """
    return generate_fhir(request)