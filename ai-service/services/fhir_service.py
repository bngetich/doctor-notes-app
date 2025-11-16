# ai-service/services/fhir_service.py

from typing import Dict, Any

from models.fhir_models import FhirRequest


def generate_fhir(payload: FhirRequest) -> Dict[str, Any]:
    """
    Build a minimal FHIR Bundle from extracted clinical entities.

    This is intentionally simple for now:
    - conditions     -> Condition
    - symptoms       -> Observation
    - medications    -> MedicationStatement
    - procedures     -> Procedure
    """

    bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": []
    }

    # Conditions -> Condition resources
    for condition in payload.conditions:
        condition_resource = {
            "resourceType": "Condition",
            "code": {
                "text": condition
            }
        }
        bundle["entry"].append({"resource": condition_resource})

    # Symptoms -> Observation resources
    for symptom in payload.symptoms:
        observation_resource = {
            "resourceType": "Observation",
            "code": {
                "text": symptom.name
            },
            "valueString": symptom.name,
        }

        # Add duration as a note if present
        if symptom.duration:
            observation_resource["note"] = [
                {"text": f"Duration: {symptom.duration}"}
            ]

        bundle["entry"].append({"resource": observation_resource})

    # Medications -> MedicationStatement resources
    for med in payload.medications:
        med_resource = {
            "resourceType": "MedicationStatement",
            "medicationCodeableConcept": {
                "text": med.name
            }
        }

        # Build a simple dosage text
        dosage_parts = []
        if med.dose:
            dosage_parts.append(med.dose)
        if med.frequency:
            dosage_parts.append(med.frequency)

        if dosage_parts:
            med_resource["dosage"] = [
                {"text": " ".join(dosage_parts)}
            ]

        bundle["entry"].append({"resource": med_resource})

    # Procedures -> Procedure resources
    for proc in payload.procedures:
        proc_resource = {
            "resourceType": "Procedure",
            "code": {
                "text": proc
            }
        }
        bundle["entry"].append({"resource": proc_resource})

    return bundle
