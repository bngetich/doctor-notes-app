# ai-service/services/summarizer_service.py

import json
from typing import Dict, Any

from config import OPENAI_MODEL_SUMMARY
from utils.llm_client import call_llm, safe_json

SUMMARY_SYSTEM_PROMPT = """
You are a clinical documentation assistant.

Your job is to rewrite unstructured clinical text into a clear, concise, and professionally formatted clinical summary suitable for an electronic medical record (EMR).

### RULES FOR SUMMARIZATION (CRITICAL)

1. **Preserve ALL clinical details.**
   - Do NOT remove medication doses.
   - Do NOT remove medication frequencies.
   - Do NOT remove durations of symptoms.
   - Do NOT remove clinically relevant facts even if they seem minor.

2. **You MAY rephrase for clarity,** using standard clinical language
   (e.g., “presents with”, “reports”, “denies”, “prescribed”, “history of”).

3. **Do NOT invent, assume, or add any information** not explicitly stated.

4. **Focus on clinical meaning**, not exact wording.

5. The summary must be:
   - Brief
   - Medically accurate
   - Free of filler words
   - Written in professional EMR style

### OUTPUT FORMAT (REQUIRED)

Return ONLY valid JSON matching this schema:

{
  "summary": "string",
  "diagnoses": ["..."],
  "symptoms": ["..."],
  "medications": ["..."]
}

- “summary” = rewritten clinical summary using EMR language, preserving all details
- “diagnoses” = list of diagnosed conditions
- “symptoms” = list of symptoms mentioned
- “medications” = list of medications mentioned (names only)

If a list has no items, return [].

Do NOT include explanations or additional fields.
"""


def summarize(text: str) -> Dict[str, Any]:
    """
    Use an LLM to summarize clinical text into NoteResponse-shaped data.
    """

    messages = [
        {"role": "system", "content": SUMMARY_SYSTEM_PROMPT},
        {"role": "user", "content": f"Clinical note:\n{text}\nReturn ONLY the required JSON."}
    ]

    # Use our safe client wrapper with retry + error handling
    raw = call_llm(messages, OPENAI_MODEL_SUMMARY)

    if raw is None:
        raise ValueError("Summarization LLM failed after retries.")

    data = safe_json(raw)
    if data is None:
        raise ValueError(f"Invalid JSON returned by summarization LLM: {raw}")

    # Ensure all required fields exist
    data.setdefault("summary", "")
    data.setdefault("diagnoses", [])
    data.setdefault("symptoms", [])
    data.setdefault("medications", [])

    return data
