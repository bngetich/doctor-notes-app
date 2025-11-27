from services.pipeline_service import normalize_entities
from models.extract_models import ExtractResponse

def test_normalization_basic():
    # BEFORE normalization: raw dictionary, messy values
    raw_entities = {
        "conditions": [" diabetes ", None, ""],
        "symptoms": [
            {"name": "   fatigue   ", "duration": "3 weeks", "severity": None},
            {"name": "", "duration": None, "severity": None},
        ],
        "medications": [
            {"name": "Metformin", "dose": "500mg", "frequency": "daily"},
            {"name": None, "dose": None, "frequency": None},
        ],
        "procedures": ["   ekg   ", ""],
        "allergies": [
            {"substance": "Penicillin", "reaction": "rash"},
            {"substance": "", "reaction": None},
        ],
        "vitals": [
            {"type": "heart rate", "value": "88", "unit": "bpm"},
            {"type": "temperature", "value": "", "unit": "C"},
        ],
        "labs": [],
        "imaging": [],
        "physical_exam": [],
        "family_history": [],
        "social_history": None,
        "patient": None,
        "assessment": None,
        "plan": None,
    }

    normalized = normalize_entities(raw_entities)

    # Make sure model parses
    parsed = ExtractResponse(**normalized)

    # Assertions
    assert parsed.conditions == ["diabetes"]
    assert parsed.symptoms[0].name == "fatigue"
    assert len(parsed.symptoms) == 1  # invalid empty symptom removed

    assert parsed.medications[0].name == "Metformin"
    assert len(parsed.medications) == 1

    assert parsed.procedures == ["ekg"]

    assert parsed.allergies[0].substance == "Penicillin"
    assert len(parsed.allergies) == 1

    assert parsed.vitals[0].type == "heart rate"
