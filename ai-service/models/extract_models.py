from pydantic import BaseModel
from typing import List, Optional


class PatientInfo(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None


class Symptom(BaseModel):
    name: str
    duration: Optional[str] = None
    severity: Optional[str] = None


class Medication(BaseModel):
    name: str
    dose: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None


class Allergy(BaseModel):
    substance: str
    reaction: Optional[str] = None


class Vital(BaseModel):
    type: str
    value: str
    unit: Optional[str] = None


class LabResult(BaseModel):
    test: str
    value: Optional[str] = None
    unit: Optional[str] = None
    interpretation: Optional[str] = None


class ImagingResult(BaseModel):
    modality: str
    finding: str
    impression: Optional[str] = None


class PhysicalExamFinding(BaseModel):
    body_part: str
    finding: str


class SocialHistory(BaseModel):
    smoking_status: Optional[str] = None
    alcohol_use: Optional[str] = None
    occupation: Optional[str] = None


class FamilyHistory(BaseModel):
    condition: str
    relation: Optional[str] = None


class ClinicalAssessment(BaseModel):
    summary: Optional[str] = None


class ClinicalPlan(BaseModel):
    actions: List[str] = []


class ExtractRequest(BaseModel):
    text: str


class ExtractResponse(BaseModel):
    patient: Optional[PatientInfo] = None

    conditions: List[str] = []
    symptoms: List[Symptom] = []
    medications: List[Medication] = []
    procedures: List[str] = []
    allergies: List[Allergy] = []

    vitals: List[Vital] = []
    labs: List[LabResult] = []
    imaging: List[ImagingResult] = []
    physical_exam: List[PhysicalExamFinding] = []

    social_history: Optional[SocialHistory] = None
    family_history: List[FamilyHistory] = []

    assessment: Optional[ClinicalAssessment] = None
    plan: Optional[ClinicalPlan] = None
