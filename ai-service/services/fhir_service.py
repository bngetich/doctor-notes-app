import uuid
import logging
from typing import Dict, Any, List

from models.extract_models import ExtractResponse
from services.terminology_service import (
    resolve_condition,
    resolve_medication,
    resolve_lab,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Utilities
# ---------------------------------------------------------

def make_id() -> str:
    """Generate a random UUID for FHIR resource IDs."""
    return str(uuid.uuid4())


# ---------------------------------------------------------
# Main FHIR generator
# ---------------------------------------------------------

def generate_fhir_resource(entities: ExtractResponse) -> Dict[str, Any]:
    """
    Build a FHIR Bundle from extracted clinical entities.

    Terminology resolution is performed *here*:
    - Conditions → SNOMED / ICD (with RAG fallback inside terminology service)
    - Medications → RxNorm (deterministic)
    - Labs → LOINC (deterministic)

    Upstream models remain text-only.
    """

    bundle: Dict[str, Any] = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [],
    }

    # ---------------------------------------------------------
    # Patient
    # ---------------------------------------------------------
    patient_id = make_id()
    patient_ref = f"Patient/{patient_id}"

    patient_resource: Dict[str, Any] = {
        "resourceType": "Patient",
        "id": patient_id,
    }

    if entities.patient:
        if entities.patient.name:
            patient_resource["name"] = [{"text": entities.patient.name}]
        if entities.patient.gender:
            patient_resource["gender"] = entities.patient.gender
        if entities.patient.age is not None:
            patient_resource["extension"] = [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-age",
                    "valueAge": {
                        "value": entities.patient.age,
                        "unit": "years",
                    },
                }
            ]

    bundle["entry"].append({"resource": patient_resource})

    # ---------------------------------------------------------
    # Conditions
    # ---------------------------------------------------------
    for condition_text in entities.conditions:
        concept = resolve_condition(condition_text)

        condition_resource = {
            "resourceType": "Condition",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": concept,
        }

        bundle["entry"].append({"resource": condition_resource})

    # Assessment summary as a Condition
    if entities.assessment and entities.assessment.summary:
        concept = resolve_condition(entities.assessment.summary)

        assessment_resource = {
            "resourceType": "Condition",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": concept,
        }

        bundle["entry"].append({"resource": assessment_resource})

    # ---------------------------------------------------------
    # Symptoms → Observations
    # ---------------------------------------------------------
    for symptom in entities.symptoms:
        obs: Dict[str, Any] = {
            "resourceType": "Observation",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {"text": symptom.name},
            "valueString": symptom.name,
        }

        notes: List[Dict[str, str]] = []
        if symptom.duration:
            notes.append({"text": f"Duration: {symptom.duration}"})
        if symptom.severity:
            notes.append({"text": f"Severity: {symptom.severity}"})

        if notes:
            obs["note"] = notes

        bundle["entry"].append({"resource": obs})

    # ---------------------------------------------------------
    # Vitals → Observations
    # ---------------------------------------------------------
    for vit in entities.vitals:
        vital_obs: Dict[str, Any] = {
            "resourceType": "Observation",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {"text": vit.type},
            "valueQuantity": {},
        }

        try:
            vital_obs["valueQuantity"]["value"] = float(vit.value)
        except Exception:
            vital_obs["valueQuantity"]["value"] = vit.value

        if vit.unit:
            vital_obs["valueQuantity"]["unit"] = vit.unit

        if not vital_obs["valueQuantity"]:
            del vital_obs["valueQuantity"]

        bundle["entry"].append({"resource": vital_obs})

    # ---------------------------------------------------------
    # Labs → Observations (LOINC)
    # ---------------------------------------------------------
    for lab in entities.labs:
        lab_code = resolve_lab(lab.test)

        lab_obs: Dict[str, Any] = {
            "resourceType": "Observation",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {
                "text": lab.test,
                **({"coding": [lab_code]} if lab_code else {}),
            },
            "valueQuantity": {},
        }

        try:
            lab_obs["valueQuantity"]["value"] = float(lab.value)
        except Exception:
            lab_obs["valueQuantity"]["value"] = lab.value

        if lab.unit:
            lab_obs["valueQuantity"]["unit"] = lab.unit

        if lab.interpretation:
            lab_obs["interpretation"] = [{"text": lab.interpretation}]

        if not lab_obs["valueQuantity"]:
            del lab_obs["valueQuantity"]

        bundle["entry"].append({"resource": lab_obs})

    # ---------------------------------------------------------
    # Medications → MedicationStatement (RxNorm)
    # ---------------------------------------------------------
    for med in entities.medications:
        med_code = resolve_medication(med.name)

        med_res: Dict[str, Any] = {
            "resourceType": "MedicationStatement",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "medicationCodeableConcept": {
                "text": med.name,
                **({"coding": [med_code]} if med_code else {}),
            },
        }

        dosage_parts: List[str] = []
        if med.dose:
            dosage_parts.append(med.dose)
        if med.frequency:
            dosage_parts.append(med.frequency)
        if med.route:
            dosage_parts.append(med.route)

        if dosage_parts:
            med_res["dosage"] = [{"text": " ".join(dosage_parts)}]

        bundle["entry"].append({"resource": med_res})

    # ---------------------------------------------------------
    # Procedures
    # ---------------------------------------------------------
    for proc in entities.procedures:
        proc_res = {
            "resourceType": "Procedure",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {"text": proc},
        }
        bundle["entry"].append({"resource": proc_res})

    # ---------------------------------------------------------
    # Allergies
    # ---------------------------------------------------------
    for allergy in entities.allergies:
        al_res: Dict[str, Any] = {
            "resourceType": "AllergyIntolerance",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {"text": allergy.substance},
        }

        if allergy.reaction:
            al_res["reaction"] = [
                {
                    "description": allergy.reaction,
                    "manifestation": [{"text": allergy.reaction}],
                }
            ]

        bundle["entry"].append({"resource": al_res})

    # ---------------------------------------------------------
    # Imaging → DiagnosticReport
    # ---------------------------------------------------------
    for img in entities.imaging:
        diag: Dict[str, Any] = {
            "resourceType": "DiagnosticReport",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "status": "final",
            "code": {"text": img.modality},
            "conclusion": img.impression or img.finding,
        }

        if img.finding:
            diag["presentedForm"] = [
                {
                    "contentType": "text/plain",
                    "data": img.finding,
                }
            ]

        bundle["entry"].append({"resource": diag})

    # ---------------------------------------------------------
    # Physical Exam → Observations
    # ---------------------------------------------------------
    for exam in entities.physical_exam:
        exam_obs = {
            "resourceType": "Observation",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {"text": f"Physical exam of {exam.body_part}"},
            "valueString": exam.finding,
        }
        bundle["entry"].append({"resource": exam_obs})

    # ---------------------------------------------------------
    # Family History
    # ---------------------------------------------------------
    for fh in entities.family_history:
        fam = {
            "resourceType": "FamilyMemberHistory",
            "id": make_id(),
            "status": "completed",
            "patient": {"reference": patient_ref},
            "condition": [{"code": {"text": fh.condition}}],
        }

        if fh.relation:
            fam["relationship"] = {"text": fh.relation}

        bundle["entry"].append({"resource": fam})

    # ---------------------------------------------------------
    # Social History → Observations
    # ---------------------------------------------------------
    if entities.social_history:
        sh = entities.social_history

        if sh.smoking_status:
            bundle["entry"].append({
                "resource": {
                    "resourceType": "Observation",
                    "id": make_id(),
                    "subject": {"reference": patient_ref},
                    "category": [{"text": "social-history"}],
                    "code": {"text": "smoking status"},
                    "valueString": sh.smoking_status,
                }
            })

        if sh.alcohol_use:
            bundle["entry"].append({
                "resource": {
                    "resourceType": "Observation",
                    "id": make_id(),
                    "subject": {"reference": patient_ref},
                    "category": [{"text": "social-history"}],
                    "code": {"text": "alcohol use"},
                    "valueString": sh.alcohol_use,
                }
            })

        if sh.occupation:
            bundle["entry"].append({
                "resource": {
                    "resourceType": "Observation",
                    "id": make_id(),
                    "subject": {"reference": patient_ref},
                    "category": [{"text": "social-history"}],
                    "code": {"text": "occupation"},
                    "valueString": sh.occupation,
                }
            })

    # ---------------------------------------------------------
    # Plan → CarePlan
    # ---------------------------------------------------------
    if entities.plan and entities.plan.actions:
        care_plan = {
            "resourceType": "CarePlan",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "status": "active",
            "intent": "plan",
            "activity": [
                {"detail": {"description": action}}
                for action in entities.plan.actions
            ],
        }

        bundle["entry"].append({"resource": care_plan})

    return bundle
