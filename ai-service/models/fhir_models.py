from pydantic import BaseModel
from typing import Literal
from typing import List, Dict, Any

from models.extract_models import Symptom, Medication


class FhirRequest(BaseModel):
    conditions: List[str]
    symptoms: List[Symptom]
    medications: List[Medication]
    procedures: List[str]

class FhirResponse(BaseModel):
    resourceType: Literal["Bundle"]
    type: str
    entry: List[Dict[str, Any]]