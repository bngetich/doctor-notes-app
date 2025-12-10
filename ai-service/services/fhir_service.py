# ai-service/services/fhir_service.py

import uuid
from typing import Dict, Any, List, Optional

from models.extract_models import ExtractResponse
from services.knowledge_service import (
    lookup_snomed,
    lookup_icd10,
    lookup_rxnorm,
    lookup_loinc,
)
from rag.rag_search import rag_lookup


def make_id() -> str:
    """
    Helper to generate a random UUID string for FHIR resource IDs.
    """
    return str(uuid.uuid4())


def validate_condition_coding(term: str, coding: Dict[str, str]) -> Optional[Dict[str, str]]:
    """
    Validate a RAG-returned coding against local CSV vocabulary.

    We treat the CSV-backed lookup (lookup_snomed / lookup_icd10)
    as the source of truth.

    Rules:
      - Try to find the same concept via local lookup (by display or term)
      - If the codes match, accept the RAG coding
      - Otherwise, reject it (return None)
    """
    display = coding.get("display") or term

    # Try SNOMED
    csv_snomed = lookup_snomed(display)
    if csv_snomed and csv_snomed.get("code") == coding.get("code"):
        return coding

    # Try ICD-10
    csv_icd = lookup_icd10(display)
    if csv_icd and csv_icd.get("code") == coding.get("code"):
        return coding

    return None


def build_condition_code(term: str) -> Dict[str, Any]:
    """
    Build the FHIR 'code' object for a Condition, using:

      1. RAG semantic search (rag_lookup) for SNOMED/ICD candidates
      2. Validation against CSV vocabulary (validate_condition_coding)
      3. Fallback to direct lookup_snomed / lookup_icd10

    Returns a dict like:
      {
        "text": "type 2 diabetes",
        "coding": [
          {...SNOMED...},
          {...ICD-10...}
        ]
      }
    """
    code_obj: Dict[str, Any] = {"text": term}
    coding_list: List[Dict[str, str]] = []

    # ------- 1. Try RAG semantic search -------
    rag_results = rag_lookup(term) or []  # assumed: list of {system, code, display}

    if rag_results:
        best_candidate = rag_results[0]
        validated = validate_condition_coding(term, best_candidate)
        if validated:
            coding_list.append(validated)

    # ------- 2. Fallback to SNOMED / ICD-10 lookups -------
    if not coding_list:
        snomed = lookup_snomed(term)
        if snomed:
            coding_list.append(snomed)

    # ICD-10 can be added alongside SNOMED
    icd10 = lookup_icd10(term)
    if icd10:
        coding_list.append(icd10)

    if coding_list:
        code_obj["coding"] = coding_list

    return code_obj


def build_lab_code(test_name: str) -> Dict[str, Any]:
    """
    Build code object for lab Observations using LOINC when possible.
    """
    code_obj: Dict[str, Any] = {"text": test_name}

    loinc = lookup_loinc(test_name)
    if loinc:
        code_obj["coding"] = [loinc]

    return code_obj


def build_medication_code(med_name: str) -> Dict[str, Any]:
    """
    Build medicationCodeableConcept using RxNorm where available.
    """
    med_code: Dict[str, Any] = {"text": med_name}

    rx = lookup_rxnorm(med_name)
    if rx:
        med_code["coding"] = [rx]

    return med_code


def generate_fhir_resource(entities: ExtractResponse) -> Dict[str, Any]:
    """
    Build a FHIR Bundle with UUID-based resources, linked Patient references,
    and terminology coding supported by both:
      - semantic RAG search (for conditions)
      - local CSV-backed lookup (SNOMED, ICD-10, LOINC, RxNorm)

    Includes:
      - Patient
      - Condition (problems + assessment)
      - Observation (symptoms, vitals, labs, physical exam, social history)
      - MedicationStatement
      - Procedure
      - AllergyIntolerance
      - DiagnosticReport
      - FamilyMemberHistory
      - CarePlan
    """

    # -----------------------------------------
    # Bundle container
    # -----------------------------------------
    bundle: Dict[str, Any] = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [],
    }

    # -----------------------------------------
    # Create Patient resource
    # -----------------------------------------
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

    # ============================================================
    # 1. CONDITIONS  (RAG + SNOMED + ICD-10)
    # ============================================================
    for condition in entities.conditions:
        condition_resource = {
            "resourceType": "Condition",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": build_condition_code(condition),
        }
        bundle["entry"].append({"resource": condition_resource})

    # Assessment summary → also a Condition
    if entities.assessment and entities.assessment.summary:
        summary_text = entities.assessment.summary
        assessment_resource = {
            "resourceType": "Condition",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": build_condition_code(summary_text),
        }
        bundle["entry"].append({"resource": assessment_resource})

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

        notes: List[Dict[str, str]] = []
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
        vital_obs: Dict[str, Any] = {
            "resourceType": "Observation",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": {"text": vit.type},
            "valueQuantity": {},
        }

        if vit.value is not None:
            try:
                vital_obs["valueQuantity"]["value"] = float(vit.value)
            except Exception:
                vital_obs["valueQuantity"]["value"] = vit.value

        if vit.unit:
            vital_obs["valueQuantity"]["unit"] = vit.unit

        if not vital_obs["valueQuantity"]:
            del vital_obs["valueQuantity"]

        bundle["entry"].append({"resource": vital_obs})

    # ============================================================
    # 4. LABS → Observations (LOINC when possible)
    # ============================================================
    for lab in entities.labs:
        lab_obs: Dict[str, Any] = {
            "resourceType": "Observation",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "code": build_lab_code(lab.test),
            "valueQuantity": {},
        }

        if lab.value is not None:
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

    # ============================================================
    # 5. MEDICATIONS → MedicationStatement (RxNorm when possible)
    # ============================================================
    for med in entities.medications:
        med_res: Dict[str, Any] = {
            "resourceType": "MedicationStatement",
            "id": make_id(),
            "subject": {"reference": patient_ref},
            "medicationCodeableConcept": build_medication_code(med.name),
        }

        dosage_parts: List[str] = []
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
    # 6. PROCEDURES → Procedure
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
            al_res["reaction"] = [
                {
                    "description": allergy.reaction,
                    "manifestation": [{"text": allergy.reaction}],
                }
            ]

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
            diag["presentedForm"] = [
                {
                    "contentType": "text/plain",
                    "data": img.finding,
                }
            ]

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
            "valueString": exam.finding,
        }
        bundle["entry"].append({"resource": exam_obs})

    # ============================================================
    # 10. FAMILY HISTORY → FamilyMemberHistory
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
    # 11. SOCIAL HISTORY → Observations (social-history category)
    # ============================================================
    if entities.social_history:
        sh = entities.social_history

        if sh.smoking_status:
            bundle["entry"].append(
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": make_id(),
                        "subject": {"reference": patient_ref},
                        "category": [{"text": "social-history"}],
                        "code": {"text": "smoking status"},
                        "valueString": sh.smoking_status,
                    }
                }
            )

        if sh.alcohol_use:
            bundle["entry"].append(
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": make_id(),
                        "subject": {"reference": patient_ref},
                        "category": [{"text": "social-history"}],
                        "code": {"text": "alcohol use"},
                        "valueString": sh.alcohol_use,
                    }
                }
            )

        if sh.occupation:
            bundle["entry"].append(
                {
                    "resource": {
                        "resourceType": "Observation",
                        "id": make_id(),
                        "subject": {"reference": patient_ref},
                        "category": [{"text": "social-history"}],
                        "code": {"text": "occupation"},
                        "valueString": sh.occupation,
                    }
                }
            )

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
            ],
        }
        bundle["entry"].append({"resource": care_plan})

    return bundle
