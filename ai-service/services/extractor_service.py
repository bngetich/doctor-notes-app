# ai-service/services/extractor_service.py

import json
from typing import Dict, Any

from fastapi import HTTPException

from config import client, OPENAI_MODEL_EXTRACT

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


def extract_entities(text: str) -> Dict[str, Any]:
    """
    Use an LLM to extract structured clinical entities
    that match the ExtractResponse Pydantic model.
    """

    user_prompt = f"""
Clinical note:

{text}

Return ONLY JSON that matches the required schema.
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL_EXTRACT,
        messages=[
            {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # For now fail loudly so you can see what the model returned
        raise HTTPException(status_code=500, detail=f"Invalid JSON from extraction LLM: {raw}")

    # Ensure all keys exist with safe defaults so Pydantic is happy
    data.setdefault("patient", None)

    data.setdefault("conditions", [])
    data.setdefault("symptoms", [])
    data.setdefault("medications", [])
    data.setdefault("procedures", [])
    data.setdefault("allergies", [])

    data.setdefault("vitals", [])
    data.setdefault("labs", [])
    data.setdefault("imaging", [])
    data.setdefault("physical_exam", [])

    data.setdefault("social_history", None)
    data.setdefault("family_history", [])

    data.setdefault("assessment", None)
    data.setdefault("plan", None)

    return data
