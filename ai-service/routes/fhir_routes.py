from fastapi import APIRouter
from models.fhir_models import FhirBundleResponse
from models.extract_models import ExtractResponse 
from services.fhir_service import generate_fhir_resource


router = APIRouter(tags=["FHIR"])

@router.post(
    "/fhir",
    response_model=FhirBundleResponse,
    summary="Generate FHIR Bundle"
)
def generate_fhir_bundle(request: ExtractResponse):
    """
    Take structured clinical entities and build a FHIR Bundle.
    """
    return generate_fhir_resource(request)