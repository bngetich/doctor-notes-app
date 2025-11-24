from services.fhir_service import generate_fhir_resource
from models.extract_models import ExtractResponse

def test_generate_full_fhir_bundle(): 
    entities = ExtractResponse(
        patient={"name": "John Doe", "age": 54, "gender": "male"},
        conditions=["Type 2 Diabetes Mellitus"],
        symptoms=[{"name": "fatigue", "duration": "3 weeks", "severity": "moderate"}],
        medications=[{"name": "Metformin", "dose": "500mg", "frequency": "daily", "route": "oral"}],
        procedures=["EKG"],
        allergies=[{"substance": "Penicillin", "reaction": "rash"}],
        vitals=[{"type": "heart rate", "value": "88", "unit": "bpm"}],
        labs=[{"test": "HbA1c", "value": "7.4", "unit": "%", "interpretation": "high"}],
        imaging=[{"modality": "Chest X-ray", "finding": "No acute infiltrates", "impression": "Normal"}],
        physical_exam=[{"body_part": "lungs", "finding": "clear"}],
        social_history={"smoking_status": "former smoker", "alcohol_use": "social", "occupation": "construction worker"},
        family_history=[{"condition": "heart disease", "relation": "father"}],
        assessment={"summary": "Likely poor glycemic control"},
        plan={"actions": ["Increase Metformin dose"]}
    )
    
    bundle = generate_fhir_resource(entities)
    
    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "collection"
    assert len(bundle["entry"]) > 0
    
    resource_types = [entry["resource"]["resourceType"]  for entry in bundle["entry"]]
    
    # Validate presence of key resources
    assert "Patient" in resource_types
    assert "Condition" in resource_types
    assert "Observation" in resource_types
    assert "MedicationStatement" in resource_types
    assert "Procedure" in resource_types
    assert "AllergyIntolerance" in resource_types
    assert "DiagnosticReport" in resource_types
    assert "FamilyMemberHistory" in resource_types
    assert "CarePlan" in resource_types