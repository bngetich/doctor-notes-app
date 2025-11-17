from pydantic import BaseModel
from typing import Optional

from models.extract_models import ExtractResponse
from models.fhir_models import FhirResponse


class PipelineRequest(BaseModel):
    text: str

class PipelineResponse(BaseModel):
    summary: Optional[str]
    entities: ExtractResponse
    fhir: FhirResponse