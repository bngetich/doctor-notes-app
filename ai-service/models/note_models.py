from pydantic import BaseModel
from typing import List

class NoteRequest(BaseModel):
    text: str
    
class NoteResponse(BaseModel):
    summary: str
    diagnoses: List[str]
    symptoms: List[str]
    medications: List[str]
