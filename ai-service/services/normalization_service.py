from typing import Dict, Any, Optional


# -----------------------
# Helper functions
# -----------------------

def normalize_string(value: Optional[str]) -> Optional[str]:
    """Trim whitespace. Convert empty strings to None."""
    if value is None:
        return None
    value = value.strip()
    return value if value else None


def normalize_case(value: Optional[str]) -> Optional[str]:
    """Lowercase standardized categories (gender, severity, etc.)."""
    if value is None:
        return None
    return value.strip().lower()


def split_value_unit(value: str):
    """Split '88 bpm' → ('88', 'bpm') if possible."""
    if not value or not isinstance(value, str):
        return value, None

    parts = value.split()
    if len(parts) == 2:
        return parts[0], parts[1]
    return value, None


# -----------------------
# Main normalization
# -----------------------

def normalize_entities(entities: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and standardize LLM-extracted entities BEFORE FHIR generation.
    This ensures FHIR generation does not crash or hallucinate.
    """

    # ------------------------------------------------------
    # CONDITIONS (List[str])
    # ------------------------------------------------------
    cleaned_conditions = []
    for c in entities.get("conditions", []):
        norm = normalize_string(c)
        if norm:
            cleaned_conditions.append(norm)
    entities["conditions"] = cleaned_conditions

    # ------------------------------------------------------
    # PROCEDURES (List[str])
    # ------------------------------------------------------
    cleaned_procedures = []
    for p in entities.get("procedures", []):
        norm = normalize_string(p)
        if norm:
            cleaned_procedures.append(norm)
    entities["procedures"] = cleaned_procedures

    # ------------------------------------------------------
    # PATIENT (Optional[dict])
    # ------------------------------------------------------
    if entities.get("patient"):
        patient = entities["patient"]

        patient_name = normalize_string(patient.get("name"))
        patient_gender = normalize_case(patient.get("gender"))

        # Age → int or None
        age_raw = patient.get("age")
        if age_raw is not None:
            try:
                age_raw = int(age_raw)
            except (ValueError, TypeError):
                age_raw = None

        entities["patient"] = {
            "name": patient_name,
            "age": age_raw,
            "gender": patient_gender
        }

    # ------------------------------------------------------
    # SYMPTOMS (List[dict])
    # ------------------------------------------------------
    cleaned_symptoms = []
    for sym in entities.get("symptoms", []):
        name = normalize_string(sym.get("name"))
        duration = normalize_string(sym.get("duration"))
        severity = normalize_case(sym.get("severity"))

        if name:  # required
            cleaned_symptoms.append({
                "name": name,
                "duration": duration,
                "severity": severity
            })
    entities["symptoms"] = cleaned_symptoms

    # ------------------------------------------------------
    # MEDICATIONS (List[dict])
    # ------------------------------------------------------
    cleaned_meds = []
    for med in entities.get("medications", []):
        name = normalize_string(med.get("name"))
        dose = normalize_string(med.get("dose"))
        frequency = normalize_case(med.get("frequency"))
        route = normalize_case(med.get("route"))

        if name:  # required
            cleaned_meds.append({
                "name": name,
                "dose": dose,
                "frequency": frequency,
                "route": route,
            })
    entities["medications"] = cleaned_meds

    # ------------------------------------------------------
    # ALLERGIES (List[dict])
    # ------------------------------------------------------
    cleaned_allergies = []
    for allergy in entities.get("allergies", []):
        substance = normalize_string(allergy.get("substance"))
        reaction = normalize_string(allergy.get("reaction"))

        if substance:  # required
            cleaned_allergies.append({
                "substance": substance,
                "reaction": reaction
            })
    entities["allergies"] = cleaned_allergies

    # ------------------------------------------------------
    # VITALS (List[dict])
    # ------------------------------------------------------
    cleaned_vitals = []
    for vit in entities.get("vitals", []):
        vtype = normalize_string(vit.get("type"))
        value = normalize_string(vit.get("value"))
        unit = normalize_string(vit.get("unit"))

        # Try splitting "88 bpm"
        if value and isinstance(value, str) and " " in value:
            split_val, split_unit = split_value_unit(value)
            value = normalize_string(split_val)
            if not unit:
                unit = normalize_string(split_unit)

        if vtype and value:  # both required
            cleaned_vitals.append({
                "type": vtype,
                "value": value,
                "unit": unit
            })
    entities["vitals"] = cleaned_vitals

    # ------------------------------------------------------
    # LAB RESULTS (List[dict])
    # ------------------------------------------------------
    cleaned_labs = []
    for lab in entities.get("labs", []):
        test = normalize_string(lab.get("test"))
        unit = normalize_string(lab.get("unit"))
        interp = normalize_case(lab.get("interpretation"))

        value = lab.get("value")
        if value is not None:
            try:
                value = float(value)
            except (ValueError, TypeError):
                value = normalize_string(value)

        if test:
            cleaned_labs.append({
                "test": test,
                "value": value,
                "unit": unit,
                "interpretation": interp
            })
    entities["labs"] = cleaned_labs

    # ------------------------------------------------------
    # SOCIAL HISTORY (Optional[dict])
    # ------------------------------------------------------
    sh = entities.get("social_history")
    if sh:
        smoking = normalize_case(sh.get("smoking_status"))
        alcohol = normalize_case(sh.get("alcohol_use"))
        occupation = normalize_string(sh.get("occupation"))

        if smoking or alcohol or occupation:
            entities["social_history"] = {
                "smoking_status": smoking,
                "alcohol_use": alcohol,
                "occupation": occupation
            }
        else:
            entities["social_history"] = None

    # ------------------------------------------------------
    # PHYSICAL EXAM (List[dict])
    # ------------------------------------------------------
    cleaned_exam = []
    for exam in entities.get("physical_exam", []):
        body = normalize_string(exam.get("body_part"))
        finding = normalize_string(exam.get("finding"))

        if body and finding:
            cleaned_exam.append({"body_part": body, "finding": finding})
    entities["physical_exam"] = cleaned_exam

    # ------------------------------------------------------
    # IMAGING (List[dict])
    # ------------------------------------------------------
    cleaned_imaging = []
    for img in entities.get("imaging", []):
        modality = normalize_string(img.get("modality"))
        finding = normalize_string(img.get("finding"))
        impression = normalize_string(img.get("impression"))

        if modality and finding:
            cleaned_imaging.append({
                "modality": modality,
                "finding": finding,
                "impression": impression
            })
    entities["imaging"] = cleaned_imaging

    # ------------------------------------------------------
    # FAMILY HISTORY (List[dict])
    # ------------------------------------------------------
    cleaned_fh = []
    for fh in entities.get("family_history", []):
        cond = normalize_string(fh.get("condition"))
        rel = normalize_string(fh.get("relation"))

        if cond:
            cleaned_fh.append({"condition": cond, "relation": rel})
    entities["family_history"] = cleaned_fh

    # ------------------------------------------------------
    # ASSESSMENT (Optional[dict])
    # ------------------------------------------------------
    if entities.get("assessment"):
        summary = normalize_string(entities["assessment"].get("summary"))
        entities["assessment"] = {"summary": summary} if summary else None

    # ------------------------------------------------------
    # PLAN (Optional[dict])
    # ------------------------------------------------------
    if entities.get("plan") and entities["plan"].get("actions"):
        actions = []
        for a in entities["plan"]["actions"]:
            norm = normalize_string(a)
            if norm:
                actions.append(norm)

        entities["plan"] = {"actions": actions} if actions else None

    return entities
