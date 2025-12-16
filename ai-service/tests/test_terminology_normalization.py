from services.knowledge_service import lookup_snomed
from services.knowledge_service import lookup_loinc
from services.knowledge_service import lookup_rxnorm


def test_snomed_normalization_parenthetical():
    result = lookup_snomed("Type 2 Diabetes (adult)")

    assert result is not None
    assert result["system"] == "http://snomed.info/sct"
    assert result["code"] == "44054006"

def test_snomed_normalization_roman_numerals():
    result = lookup_snomed("Type-II diabetes")

    assert result is not None
    assert result["code"] == "44054006"


def test_loinc_normalization_symbols():
    result = lookup_loinc("HbA1c (%)")

    assert result is not None
    assert result["system"] == "http://loinc.org"


def test_rxnorm_normalization_dosage():
    result = lookup_rxnorm("Metformin 500mg")

    assert result is not None
    assert result["display"].lower() == "metformin"



