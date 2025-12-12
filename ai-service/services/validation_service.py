# ai-service/services/validation_service.py

from typing import Dict, Any
from fastapi import HTTPException


def validate_entities(entities: Dict[str, Any]) -> None:
    """
    Top-level validation function.
    Raises HTTPException if validation fails.
    """

    conditions = entities.get("conditions", [])
    symptoms = entities.get("symptoms", [])
    medications = entities.get("medications", [])
    vitals = entities.get("vitals", [])
    labs = entities.get("labs", [])
    imaging = entities.get("imaging", [])
    procedures = entities.get("procedures", [])

    # 1. Conditions must be non-empty strings
    for c in conditions:
        if not isinstance(c, str) or not c.strip():
            raise HTTPException(
                status_code=400,
                detail=f"Invalid condition value: '{c}'"
            )

    # 2. Medications must have a name
    for med in medications:
        if not med.get("name"):
            raise HTTPException(
                status_code=400,
                detail="Medication entry missing 'name'"
            )

    # 3. Labs must have a test name
    for lab in labs:
        if not lab.get("test"):
            raise HTTPException(
                status_code=400,
                detail="Lab entry missing 'test'"
            )

    # 4. Vitals must have type + value
    for vit in vitals:
        if not vit.get("type") or vit.get("value") is None:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid vital entry: {vit}"
            )

    # 5. Guardrail: reject empty clinical payloads
    if not any([
        conditions,
        symptoms,
        medications,
        vitals,
        labs,
        imaging,
        procedures,
    ]):
        raise HTTPException(
            status_code=422,
            detail="No structured clinical entities were extracted from the note."
        )
