from unittest.mock import patch
from services.extractor_service import extract_entities


def test_extractor_valid_json():
    mock_output = """
    {
        "patient": {"name": "John", "age": 30, "gender": "male"},
        "conditions": ["diabetes"],
        "symptoms": [],
        "medications": [],
        "procedures": [],
        "allergies": [],
        "vitals": [],
        "labs": [],
        "imaging": [],
        "physical_exam": [],
        "social_history": null,
        "family_history": [],
        "assessment": null,
        "plan": null
    }
    """

    with patch("services.extractor_service.call_llm", return_value=mock_output):
        result = extract_entities("test clinical note")

    assert result["patient"]["name"] == "John"
    assert result["conditions"] == ["diabetes"]

    