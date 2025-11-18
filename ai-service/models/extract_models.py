# ai-service/models/extract.py

from pydantic import BaseModel
from typing import List, Optional


class Symptom(BaseModel):
    name: str
    duration: Optional[str] = None


class Medication(BaseModel):
    name: str
    dose: Optional[str] = None
    frequency: Optional[str] = None
    
class ExtractRequest(BaseModel):
    text: str

class ExtractResponse(BaseModel):
    conditions: List[str]
    symptoms: List[Symptom]
    medications: List[Medication]
    procedures: List[str]
