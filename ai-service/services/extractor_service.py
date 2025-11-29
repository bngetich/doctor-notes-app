# ai-service/services/extractor_service.py

import json
from typing import Dict, Any

from fastapi import HTTPException

from utils.llm_client import call_llm, safe_json
from config import OPENAI_MODEL_EXTRACT

EXTRACT_SYSTEM_PROMPT = """
You are a clinical information extraction model.

You extract structured data from doctor-patient encounter notes.

You MUST return ONLY valid JSON that matches this schema:

{
  "patient": {
    "name": string or null,
    "age": integer or null,
    "gender": string or null
  } or null,

  "conditions": [string, ...],

  "symptoms": [
    {
      "name": string,
      "duration": string or null,
      "severity": string or null
    },
    ...
  ],

  "medications": [
    {
      "name": string,
      "dose": string or null,
      "frequency": string or null,
      "route": string or null
    },
    ...
  ],

  "procedures": [string, ...],

  "allergies": [
    {
      "substance": string,
      "reaction": string or null
    },
    ...
  ],

  "vitals": [
    {
      "type": string,
      "value": string,
      "unit": string or null
    },
    ...
  ],

  "labs": [
    {
      "test": string,
      "value": string or null,
      "unit": string or null,
      "interpretation": string or null
    },
    ...
  ],

  "imaging": [
    {
      "modality": string,
      "finding": string,
      "impression": string or null
    },
    ...
  ],

  "physical_exam": [
    {
      "body_part": string,
      "finding": string
    },
    ...
  ],

  "social_history": {
    "smoking_status": string or null,
    "alcohol_use": string or null,
    "occupation": string or null
  } or null,

  "family_history": [
    {
      "condition": string,
      "relation": string or null
    },
    ...
  ],

  "assessment": {
    "summary": string or null
  } or null,

  "plan": {
    "actions": [string, ...]
  } or null
}

Rules:
- If a list has no items, return an empty list [].
- If an object has no data, return null for that object.
- Never invent medical facts that are not clearly stated in the note.
- Do NOT include any extra top-level fields besides those listed.
- Do NOT return any explanation. Return ONLY JSON.
"""


def _call_extraction_llm(text: str) -> str:
    """
    Single extraction request.
    Uses call_llm() which includes tenacity retries.
    """
    user_prompt = f"""
Clinical note:

{text}

Return ONLY JSON that matches the required schema.
"""

    raw = call_llm(
        messages=[
            {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        model=OPENAI_MODEL_EXTRACT,
    )

    if raw is None:
        # All tenacity retries failed
        raise HTTPException(
            status_code=500, detail="Extraction LLM failed after retries."
        )

    return raw.strip()


def _call_repair_llm(bad_output: str) -> str:
    """
    Use LLM to fix invalid JSON.
    Also uses call_llm() for retry/backoff.
    """

    repair_prompt = f"""
The following content is invalid JSON:

{bad_output}

Fix it so it becomes valid JSON matching the required extraction schema.
Return ONLY the corrected JSON.
"""

    raw = call_llm(
        messages=[
            {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
            {"role": "user", "content": repair_prompt},
        ],
        model=OPENAI_MODEL_EXTRACT,
    )

    if raw is None:
        raise HTTPException(status_code=500, detail="Repair LLM failed after retries.")

    return raw.strip()


def extract_entities(text: str) -> Dict[str, Any]:
    """
    Robust extraction with:
    - Tenacity API retry layer (via call_llm)
    - LLM JSON repair layer if initial attempt fails
    """

    last_raw = None
    parsed_data = None

    # Two-attempt strategy:
    # 1. Normal extraction
    # 2. Repair JSON
    for attempt in range(2):

        if attempt == 0:
            raw = _call_extraction_llm(text)
        else:
            raw = _call_repair_llm(last_raw or "")

        last_raw = raw

        loaded = safe_json(raw)
        if isinstance(loaded, dict):
            parsed_data = loaded
            break

    if parsed_data is None:
        raise HTTPException(
            status_code=500,
            detail=f"Invalid JSON from extraction LLM after repair attempts: {last_raw}",
        )

    # Safety defaults for missing fields
    defaults = {
        "patient": None,
        "conditions": [],
        "symptoms": [],
        "medications": [],
        "procedures": [],
        "allergies": [],
        "vitals": [],
        "labs": [],
        "imaging": [],
        "physical_exam": [],
        "social_history": None,
        "family_history": [],
        "assessment": None,
        "plan": None,
    }

    for key, default in defaults.items():
        parsed_data.setdefault(key, default)

    return parsed_data
