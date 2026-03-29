"""Tests for medical coding verification."""

from src.coding_verifier import audit_coding, determine_supported_mdm_level


def test_determine_supported_mdm_level_uses_two_of_three_rule():
    level = determine_supported_mdm_level(
        problems="moderate",
        data="low",
        risk="moderate",
    )

    assert level.label() == "moderate"


def test_audit_coding_flags_em_cci_and_icd10_issues():
    payload = {
        "visit_id": "visit-001",
        "encounter_type": "established_office",
        "transcript": (
            "Established patient follow-up for type 2 diabetes with chronic kidney disease "
            "stage 3a and hypertension. Reviewed CMP and A1c. Continued lisinopril and "
            "metformin. No acute distress, no hospitalization discussed."
        ),
        "coding_output": {
            "em_code": "99215",
            "cpt_codes": [
                {"code": "99215", "modifiers": [], "description": "Established patient office visit"},
                {"code": "93000", "modifiers": [], "description": "Electrocardiogram complete"},
                {"code": "93010", "modifiers": [], "description": "ECG interpretation"},
            ],
            "icd10_codes": [
                {"code": "E11.9", "description": "Type 2 diabetes mellitus without complications"},
                {"code": "N18.9", "description": "Chronic kidney disease, unspecified"},
                {"code": "I10", "description": "Essential hypertension"},
            ],
        },
        "clinical_context": {
            "mdm": {
                "problems": "moderate",
                "data": "low",
                "risk": "moderate",
            },
            "diagnoses_documented": [
                {
                    "label": "Type 2 diabetes mellitus with diabetic chronic kidney disease",
                    "keywords": ["type 2 diabetes", "chronic kidney disease"],
                    "expected_icd10": ["E11.22"],
                },
                {
                    "label": "Chronic kidney disease stage 3a",
                    "keywords": ["stage 3a"],
                    "expected_icd10": ["N18.31"],
                },
            ],
            "procedures_documented": [],
        },
    }

    result = audit_coding(payload).to_dict()

    assert result["recommended_em_code"] == "99214"
    assert result["status"] == "fail"
    messages = [issue["message"] for issue in result["issues"]]
    assert any("upcoding" in message for message in messages)
    assert any("ECG tracing/report" in message for message in messages)
    assert any("E11.22" in (issue["suggested_fix"] or "") for issue in result["issues"])
