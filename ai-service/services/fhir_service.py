# ai-service/services/fhir_service.py

import uuid
from typing import Dict, Any

from models.extract_models import ExtractResponse
from services.knowledge_service import (
    lookup_snomed,
    lookup_icd10,
    lookup_rxnorm,
    lookup_loinc,
)


def generate_fhir_resource(entities: ExtractResponse) -> Dict[str, Any]:
    """
    Build a FHIR Bundle with UUID-based resources, linked Patient references,
    and support for all extracted clinical entities.

    Now includes:
      - SNOMED + ICD-10 coding for conditions (when available)
      - RxNorm coding for medications
      - LOINC coding for lab tests
    """

    # -----------------------------------------
    # Bundle container
    # -----------------------------------------
    bundle: Dict[str, Any] = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": []
    }

    # UUID helper
    def make_id() -> str:
        return str(uuid.uuid4())

    # -----------------------------------------
    # Create Patient resource with UUID
    # -----------------------------------------
    patient_id = make_id()

    patient_resource: Dict[str, Any] = {
        "resourceType": "Patient",
        "id": patient_id
    }

    # Add demographics if provided
    if entities.patient:
        if entities.patient.name:
            patient_resource["name"] = [{"text": entities.patient.name}]

        if entities.patient.gender:
            patient_resource["gender"] = entities.patient.gender

        if entities.patient.age is not None:
            # Age stored as extension
            patient_resource["extension"] = [
                {
                    "url": "http://hl7.org/fhir/StructureDefinition/patient-age",
                    "valueAge": {
                        "value": entities.patient.age,
                        "unit": "years"
                    }
                }
            ]

    # Add the Patient entry
    bundle["entry"].append({"resource": patient_resource})

    # Convenience reference string
    patient_ref = f"Patient/{patient_id}"

    # ============================================================
    # 1. CONDITIONS  (SNOMED + ICD-10 when possible)
    # ============================================================
    for condition in entities.conditions:
        # Try SNOMED first, then ICD-10 as fallback
        coding = lookup_snomed(condition) or lookup_icd10(condition)

        resource = {
            "resourceType": "Condition",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {
                "text": condition
            }
        }
        # If we found a coding, add it under code.coding
        if coding:
            resource["code"]["coding"] = [coding]

        bundle["entry"].append({"resource": resource})

    # Assessment summary → treat as Condition (problem/assessment)
    if entities.assessment and entities.assessment.summary:
        summary_text = entities.assessment.summary
        code_obj: Dict[str, Any] = {"text": summary_text}
        coding_array = []

        snomed = lookup_snomed(summary_text)
        if snomed:
            coding_array.append(snomed)

        icd10 = lookup_icd10(summary_text)
        if icd10:
            coding_array.append(icd10)

        if coding_array:
            code_obj["coding"] = coding_array

        resource = {
            "resourceType": "Condition",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": code_obj,
        }
        bundle["entry"].append({"resource": resource})

    # ============================================================
    # 2. SYMPTOMS → Observations
    # ============================================================
    for symptom in entities.symptoms:
        obs: Dict[str, Any] = {
            "resourceType": "Observation",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {"text": symptom.name},
            "valueString": symptom.name,
        }

        notes = []
        if symptom.duration:
            notes.append({"text": f"Duration: {symptom.duration}"})
        if symptom.severity:
            notes.append({"text": f"Severity: {symptom.severity}"})
        if notes:
            obs["note"] = notes

        bundle["entry"].append({"resource": obs})

    # ============================================================
    # 3. VITALS → Observations
    # ============================================================
    for vit in entities.vitals:
        obs: Dict[str, Any] = {
            "resourceType": "Observation",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {"text": vit.type},
            "valueQuantity": {}
        }

        if vit.value is not None:
            try:
                obs["valueQuantity"]["value"] = float(vit.value)
            except Exception:
                obs["valueQuantity"]["value"] = vit.value

        if vit.unit:
            obs["valueQuantity"]["unit"] = vit.unit

        if not obs["valueQuantity"]:
            del obs["valueQuantity"]

        bundle["entry"].append({"resource": obs})

    # ============================================================
    # 4. LABS → Observations (LOINC when possible)
    # ============================================================
    for lab in entities.labs:
        # Try to map to LOINC
        coding = lookup_loinc(lab.test)

        obs: Dict[str, Any] = {
            "resourceType": "Observation",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {
                "text": lab.test
            },
            "valueQuantity": {}
        }

        if coding:
            obs["code"]["coding"] = [coding]

        if lab.value is not None:
            try:
                obs["valueQuantity"]["value"] = float(lab.value)
            except Exception:
                obs["valueQuantity"]["value"] = lab.value

        if lab.unit:
            obs["valueQuantity"]["unit"] = lab.unit

        if lab.interpretation:
            obs["interpretation"] = [{"text": lab.interpretation}]

        if not obs["valueQuantity"]:
            del obs["valueQuantity"]

        bundle["entry"].append({"resource": obs})

    # ============================================================
    # 5. MEDICATIONS → MedicationStatement (RxNorm when possible)
    # ============================================================
    for med in entities.medications:
        coding = lookup_rxnorm(med.name)
        med_res: Dict[str, Any] = {
            "resourceType": "MedicationStatement",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "medicationCodeableConcept": {"text": med.name},
        }

        if coding:
            med_res["medicationCodeableConcept"]["coding"] = [coding]

        dosage_parts = []
        if med.dose:
            dosage_parts.append(med.dose)
        if med.frequency:
            dosage_parts.append(med.frequency)
        if getattr(med, "route", None):
            dosage_parts.append(med.route)

        if dosage_parts:
            med_res["dosage"] = [{"text": " ".join(dosage_parts)}]

        bundle["entry"].append({"resource": med_res})

    # ============================================================
    # 6. PROCEDURES
    # ============================================================
    for proc in entities.procedures:
        proc_res = {
            "resourceType": "Procedure",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {"text": proc},
        }
        bundle["entry"].append({"resource": proc_res})

    # ============================================================
    # 7. ALLERGIES → AllergyIntolerance
    # ============================================================
    for allergy in entities.allergies:
        al_res: Dict[str, Any] = {
            "resourceType": "AllergyIntolerance",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {"text": allergy.substance},
        }

        if allergy.reaction:
            al_res["reaction"] = [{
                "description": allergy.reaction,
                "manifestation": [{"text": allergy.reaction}]
            }]

        bundle["entry"].append({"resource": al_res})

    # ============================================================
    # 8. IMAGING → DiagnosticReport
    # ============================================================
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
            diag["presentedForm"] = [{
                "contentType": "text/plain",
                "data": img.finding
            }]

        bundle["entry"].append({"resource": diag})

    # ============================================================
    # 9. PHYSICAL EXAM → Observations
    # ============================================================
    for exam in entities.physical_exam:
        exam_obs = {
            "resourceType": "Observation",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {"text": f"Physical exam of {exam.body_part}"},
            "valueString": exam.finding
        }

        bundle["entry"].append({"resource": exam_obs})

    # ============================================================
    # 10. FAMILY HISTORY
    # ============================================================
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

    # ============================================================
    # 11. SOCIAL HISTORY → Observations
    # ============================================================
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

    # ============================================================
    # 12. PLAN → CarePlan
    # ============================================================
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
            ]
        }

        bundle["entry"].append({"resource": care_plan})

    return bundle
