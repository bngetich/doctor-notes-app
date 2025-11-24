# ai-service/services/fhir_service.py

from typing import Dict, Any

from models.extract_models import ExtractResponse


def generate_fhir_resource(entities: ExtractResponse) -> Dict[str, Any]:
    """
    Build a FHIR Bundle from extracted clinical entities.

    Currently includes:
      - Patient
      - Condition (problems, assessment text)
      - Observation (symptoms, vitals, labs, physical exam, social history)
      - MedicationStatement
      - Procedure
      - AllergyIntolerance
      - DiagnosticReport (imaging)
      - FamilyMemberHistory
      - CarePlan (plan/actions)
    """

    bundle: Dict[str, Any] = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": []
    }

    # -------------------------
    # Patient → Patient
    # -------------------------
    if entities.patient:
        pat = {
            "resourceType": "Patient",
            "name": [{"text": entities.patient.name}] if entities.patient.name else None,
            "gender": entities.patient.gender,
        }

        if entities.patient.age is not None:
            pat["extension"] = [{
                "url": "http://hl7.org/fhir/StructureDefinition/patient-age",
                "valueAge": {"value": entities.patient.age, "unit": "years"}
            }]

        # Remove None fields
        pat = {k: v for k, v in pat.items() if v is not None}

        bundle["entry"].append({"resource": pat})

    # -------------------------
    # Conditions → Condition
    # -------------------------
    for condition in entities.conditions:
        condition_resource = {
            "resourceType": "Condition",
            "code": {
                "text": condition
            }
        }
        bundle["entry"].append({"resource": condition_resource})

    # Assessment summary → Condition (problem/assessment)
    if entities.assessment and entities.assessment.summary:
        bundle["entry"].append({
            "resource": {
                "resourceType": "Condition",
                "code": {"text": entities.assessment.summary}
            }
        })

    # -------------------------
    # Symptoms → Observation
    # -------------------------
    for symptom in entities.symptoms:
        observation_resource = {
            "resourceType": "Observation",
            "code": {
                "text": symptom.name
            },
            "valueString": symptom.name,
        }

        notes = []
        if symptom.duration:
            notes.append({"text": f"Duration: {symptom.duration}"})
        if symptom.severity:
            notes.append({"text": f"Severity: {symptom.severity}"})
        if notes:
            observation_resource["note"] = notes

        bundle["entry"].append({"resource": observation_resource})

    # -------------------------
    # Vitals → Observation
    # -------------------------
    for vit in entities.vitals:
        # Example: { "type": "heart rate", "value": "88", "unit": "bpm" }

        vital_obs: Dict[str, Any] = {
            "resourceType": "Observation",
            "code": {
                "text": vit.type
            },
            "valueQuantity": {}
        }

        # value (numeric or string)
        if vit.value is not None:
            try:
                vital_obs["valueQuantity"]["value"] = float(vit.value)
            except (TypeError, ValueError):
                vital_obs["valueQuantity"]["value"] = vit.value

        # unit
        if vit.unit:
            vital_obs["valueQuantity"]["unit"] = vit.unit

        # drop valueQuantity if empty
        if not vital_obs["valueQuantity"]:
            del vital_obs["valueQuantity"]

        bundle["entry"].append({"resource": vital_obs})

    # -------------------------
    # Labs → Observation
    # -------------------------
    for lab in entities.labs:
        # Example: { "test": "HbA1c", "value": "7.4", "unit": "%", "interpretation": "high" }

        lab_obs: Dict[str, Any] = {
            "resourceType": "Observation",
            "code": {
                "text": lab.test
            },
            "valueQuantity": {}
        }

        if lab.value is not None:
            try:
                lab_obs["valueQuantity"]["value"] = float(lab.value)
            except (TypeError, ValueError):
                lab_obs["valueQuantity"]["value"] = lab.value

        if lab.unit:
            lab_obs["valueQuantity"]["unit"] = lab.unit

        if lab.interpretation:
            lab_obs["interpretation"] = [
                {"text": lab.interpretation}
            ]

        if not lab_obs["valueQuantity"]:
            del lab_obs["valueQuantity"]

        bundle["entry"].append({"resource": lab_obs})

    # -------------------------
    # Medications → MedicationStatement
    # -------------------------
    for med in entities.medications:
        med_resource: Dict[str, Any] = {
            "resourceType": "MedicationStatement",
            "medicationCodeableConcept": {
                "text": med.name
            }
        }

        dosage_parts = []
        if med.dose:
            dosage_parts.append(med.dose)
        if med.frequency:
            dosage_parts.append(med.frequency)
        if getattr(med, "route", None):
            dosage_parts.append(med.route)

        if dosage_parts:
            med_resource["dosage"] = [
                {"text": " ".join(dosage_parts)}
            ]

        bundle["entry"].append({"resource": med_resource})

    # -------------------------
    # Procedures → Procedure
    # -------------------------
    for proc in entities.procedures:
        proc_resource = {
            "resourceType": "Procedure",
            "code": {
                "text": proc
            }
        }
        bundle["entry"].append({"resource": proc_resource})

    # -------------------------
    # Allergies → AllergyIntolerance
    # -------------------------
    for allergy in entities.allergies:
        allergy_resource: Dict[str, Any] = {
            "resourceType": "AllergyIntolerance",
            "code": {
                "text": allergy.substance
            }
        }

        if allergy.reaction:
            allergy_resource["reaction"] = [
                {
                    "description": allergy.reaction,
                    "manifestation": [{"text": allergy.reaction}]
                }
            ]

        bundle["entry"].append({"resource": allergy_resource})

    # -------------------------
    # Imaging → DiagnosticReport
    # -------------------------
    for img in entities.imaging:
        # Example: { "modality": "X-ray", "finding": "No fracture", "impression": "Normal study" }

        diag: Dict[str, Any] = {
            "resourceType": "DiagnosticReport",
            "status": "final",
            "code": {"text": img.modality},
            "conclusion": img.impression or img.finding,
        }

        # Attach finding as a simple presentedForm text blob
        if img.finding:
            diag["presentedForm"] = [
                {
                    "contentType": "text/plain",
                    "data": img.finding
                }
            ]

        bundle["entry"].append({"resource": diag})

    # -------------------------
    # Physical exam → Observation
    # -------------------------
    for exam in entities.physical_exam:
        exam_obs = {
            "resourceType": "Observation",
            "code": {"text": f"Physical exam of {exam.body_part}"},
            "valueString": exam.finding
        }

        bundle["entry"].append({"resource": exam_obs})

    # -------------------------
    # Family history → FamilyMemberHistory
    # -------------------------
    for fh in entities.family_history:
        fam: Dict[str, Any] = {
            "resourceType": "FamilyMemberHistory",
            "status": "completed",
            "condition": [
                {"code": {"text": fh.condition}}
            ]
        }

        if fh.relation:
            fam["relationship"] = {"text": fh.relation}

        bundle["entry"].append({"resource": fam})

    # -------------------------
    # Social history → Observation (social-history category)
    # -------------------------
    if entities.social_history:
        sh = entities.social_history

        if sh.smoking_status:
            bundle["entry"].append({
                "resource": {
                    "resourceType": "Observation",
                    "category": [{"text": "social-history"}],
                    "code": {"text": "smoking status"},
                    "valueString": sh.smoking_status
                }
            })

        if sh.alcohol_use:
            bundle["entry"].append({
                "resource": {
                    "resourceType": "Observation",
                    "category": [{"text": "social-history"}],
                    "code": {"text": "alcohol use"},
                    "valueString": sh.alcohol_use
                }
            })

        if sh.occupation:
            bundle["entry"].append({
                "resource": {
                    "resourceType": "Observation",
                    "category": [{"text": "social-history"}],
                    "code": {"text": "occupation"},
                    "valueString": sh.occupation
                }
            })

    # -------------------------
    # Plan → CarePlan
    # -------------------------
    if entities.plan and entities.plan.actions:
        care_plan = {
            "resourceType": "CarePlan",
            "status": "active",
            "intent": "plan",
            "activity": [
                {"detail": {"description": action}}
                for action in entities.plan.actions
            ]
        }
        bundle["entry"].append({"resource": care_plan})

    return bundle
