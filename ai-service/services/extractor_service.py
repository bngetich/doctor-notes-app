from typing import Dict, Any


def extract_entities(text: str) -> Dict[str, Any]:
    """
    Mock entity extractor.

    Later this will call an LLM with a two-step prompt to extract
    conditions, symptoms, medications, and procedures.
    """
    # TEMP: hardcoded example just to wire things up
    return {
        "conditions": ["Type 2 Diabetes"],
        "symptoms": [
            {"name": "fatigue", "duration": "3 weeks"}
        ],
        "medications": [
            {"name": "Metformin", "dose": "500mg", "frequency": "daily"}
        ],
        "procedures": []
    }
