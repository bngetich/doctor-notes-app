# ai-service/services/extractor_service.py

import json
from typing import Dict, Any

from config import OPENAI_MODEL_EXTRACT
from utils.llm_client import call_llm, safe_json

EXTRACT_SYSTEM_PROMPT = """
You are a clinical information extraction model.

Extract the following entities from the clinical text:

- conditions: diagnoses / diseases / chronic conditions
- symptoms: key symptoms the patient reports (include duration if mentioned)
- medications: drugs (with dose and frequency if mentioned)
- procedures: clinical or medical procedures performed or planned

Return ONLY valid JSON in exactly this format:

{
  "conditions": ["..."],
  "symptoms": [
    { "name": "...", "duration": "..." }
  ],
  "medications": [
    { "name": "...", "dose": "...", "frequency": "..." }
  ],
  "procedures": ["..."]
}

Rules:
- If there are no items for a field, return an empty list [].
- Do NOT invent information that is not clearly stated.
- Do NOT include explanations or any extra top-level fields.
"""


def extract_entities(text: str) -> Dict[str, Any]:
    """
    Use an LLM to extract structured clinical entities based on ExtractResponse schema.
    """

    messages = [
        {"role": "system", "content": EXTRACT_SYSTEM_PROMPT},
        {"role": "user", "content": f"Clinical note:\n{text}\nReturn ONLY the required JSON."}
    ]

    # Safe OpenAI call with retry + backoff
    raw = call_llm(messages, OPENAI_MODEL_EXTRACT)

    if raw is None:
        raise ValueError("Extraction LLM failed after retries.")

    data = safe_json(raw)
    if data is None:
        raise ValueError(f"Invalid JSON returned by extraction LLM: {raw}")

    # Ensure all expected fields are present
    data.setdefault("conditions", [])
    data.setdefault("symptoms", [])
    data.setdefault("medications", [])
    data.setdefault("procedures", [])

    return data
