"""Medical coding verification helpers for auditing AI-generated codes."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import json
import re
from typing import Dict, List, Optional, Sequence


class AuditSeverity(Enum):
    """Severity assigned to coding audit findings."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class MDMLevel(Enum):
    """Ordered MDM complexity levels."""

    STRAIGHTFORWARD = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4

    @classmethod
    def from_value(cls, value: str) -> "MDMLevel":
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        mapping = {
            "straightforward": cls.STRAIGHTFORWARD,
            "low": cls.LOW,
            "moderate": cls.MODERATE,
            "high": cls.HIGH,
        }
        if normalized not in mapping:
            raise ValueError(f"Unsupported MDM level: {value}")
        return mapping[normalized]

    def label(self) -> str:
        return self.name.lower()


@dataclass
class CodingIssue:
    """Individual coding issue."""

    category: str
    severity: AuditSeverity
    message: str
    details: Optional[str] = None
    suggested_fix: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        return {
            "category": self.category,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "suggested_fix": self.suggested_fix,
        }


@dataclass
class CodingAuditResult:
    """Structured coding audit output."""

    visit_id: str
    recommended_em_code: Optional[str]
    assigned_em_code: Optional[str]
    supported_mdm_level: Optional[str]
    issues: List[CodingIssue] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        severity_counts = {severity.value: 0 for severity in AuditSeverity}
        for issue in self.issues:
            severity_counts[issue.severity.value] += 1

        status = "pass"
        if severity_counts["error"]:
            status = "fail"
        elif severity_counts["warning"]:
            status = "warning"

        return {
            "visit_id": self.visit_id,
            "status": status,
            "assigned_em_code": self.assigned_em_code,
            "recommended_em_code": self.recommended_em_code,
            "supported_mdm_level": self.supported_mdm_level,
            "issue_counts": severity_counts,
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


EM_CODE_MAP = {
    "new_office": {
        MDMLevel.STRAIGHTFORWARD: "99202",
        MDMLevel.LOW: "99203",
        MDMLevel.MODERATE: "99204",
        MDMLevel.HIGH: "99205",
    },
    "established_office": {
        MDMLevel.STRAIGHTFORWARD: "99212",
        MDMLevel.LOW: "99213",
        MDMLevel.MODERATE: "99214",
        MDMLevel.HIGH: "99215",
    },
}

EM_LEVEL_BY_CODE = {
    code: level
    for encounter_map in EM_CODE_MAP.values()
    for level, code in encounter_map.items()
}

# Representative high-yield subset of same-day CCI edits commonly involved in
# outpatient audits. This is intentionally small and explainable.
CCI_BUNDLING_RULES = {
    frozenset({"93000", "93010"}): {
        "message": "ECG tracing/report and ECG interpretation were billed together.",
        "details": "CMS CCI typically allows one component or the global service, not both.",
        "suggested_fix": "Bill 93000 alone for the global ECG service, or split technical/professional components correctly.",
    },
    frozenset({"93000", "93005"}): {
        "message": "ECG global service conflicts with the technical component on the same date.",
        "details": "Global billing already includes the tracing/report portion.",
        "suggested_fix": "Remove either 93000 or 93005 unless services were separated correctly.",
    },
    frozenset({"11042", "11045"}): {
        "message": "Debridement add-on code requires correct primary-unit pairing review.",
        "details": "CCI edit review is required for wound debridement unit combinations.",
        "suggested_fix": "Confirm unit counts and primary/add-on sequencing.",
    },
}


def _level_supported_by_two_of_three(level: MDMLevel, levels: Sequence[MDMLevel]) -> bool:
    return sum(component.value >= level.value for component in levels) >= 2


def determine_supported_mdm_level(problems: str, data: str, risk: str) -> MDMLevel:
    """Determine supported MDM level using the 2-of-3 CMS framework."""

    component_levels = [
        MDMLevel.from_value(problems),
        MDMLevel.from_value(data),
        MDMLevel.from_value(risk),
    ]
    for level in reversed(list(MDMLevel)):
        if _level_supported_by_two_of_three(level, component_levels):
            return level
    return MDMLevel.STRAIGHTFORWARD


def recommended_em_code(encounter_type: str, mdm_level: MDMLevel) -> Optional[str]:
    """Return the MDM-driven office E/M code when supported."""

    normalized_type = encounter_type.strip().lower()
    return EM_CODE_MAP.get(normalized_type, {}).get(mdm_level)


def _find_code_entry(entries: Sequence[Dict[str, object]], code: str) -> Dict[str, object]:
    for entry in entries:
        if str(entry.get("code", "")).strip() == code:
            return entry
    return {}


def _transcript_contains_any(text: str, patterns: Sequence[str]) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in patterns)


def _audit_em_level(payload: Dict[str, object], issues: List[CodingIssue]) -> Optional[str]:
    mdm = payload.get("clinical_context", {}).get("mdm", {})
    encounter_type = str(payload.get("encounter_type", "")).strip().lower()
    assigned_em_code = str(payload.get("coding_output", {}).get("em_code", "")).strip() or None

    if not mdm:
        issues.append(CodingIssue(
            category="em_level",
            severity=AuditSeverity.WARNING,
            message="No structured MDM summary was provided for E/M validation.",
            suggested_fix="Include problems, data, and risk levels to support E/M auditing.",
        ))
        return None

    supported_level = determine_supported_mdm_level(
        problems=str(mdm.get("problems", "straightforward")),
        data=str(mdm.get("data", "straightforward")),
        risk=str(mdm.get("risk", "straightforward")),
    )
    recommended_code = recommended_em_code(encounter_type, supported_level)

    if assigned_em_code and recommended_code and assigned_em_code != recommended_code:
        assigned_level = EM_LEVEL_BY_CODE.get(assigned_em_code)
        severity = AuditSeverity.ERROR
        category = "upcoding_downcoding"
        direction = "upcoding" if assigned_level and assigned_level.value > supported_level.value else "downcoding"
        issues.append(CodingIssue(
            category=category,
            severity=severity,
            message=f"Assigned E/M code {assigned_em_code} suggests {direction} versus the documented MDM.",
            details=(
                f"Encounter type: {encounter_type}; documented MDM supports "
                f"{supported_level.label()} complexity and code {recommended_code}."
            ),
            suggested_fix=f"Use {recommended_code} unless additional documentation supports {assigned_em_code}.",
        ))

    transcript = str(payload.get("transcript", ""))
    if assigned_em_code == "99215" and not _transcript_contains_any(
        transcript,
        [
            "life-threatening",
            "severe exacerbation",
            "drug therapy requiring intensive monitoring",
            "decision regarding hospitalization",
        ],
    ):
        issues.append(CodingIssue(
            category="em_level",
            severity=AuditSeverity.WARNING,
            message="High-complexity established patient coding lacks obvious high-risk language in the transcript.",
            details="99215 usually needs high MDM or clearly documented high-risk management.",
            suggested_fix="Confirm the transcript and assessment document high-risk decision making.",
        ))

    return recommended_code


def _audit_cci_rules(payload: Dict[str, object], issues: List[CodingIssue]) -> None:
    code_entries = payload.get("coding_output", {}).get("cpt_codes", [])
    codes = {str(entry.get("code", "")).strip() for entry in code_entries if entry.get("code")}
    modifiers_by_code = {
        str(entry.get("code", "")).strip(): {str(mod).strip() for mod in entry.get("modifiers", [])}
        for entry in code_entries
    }

    for code_pair, rule in CCI_BUNDLING_RULES.items():
        if code_pair.issubset(codes):
            has_modifier_25 = any("25" in modifiers_by_code.get(code, set()) for code in code_pair)
            issues.append(CodingIssue(
                category="cci_rules",
                severity=AuditSeverity.ERROR if not has_modifier_25 else AuditSeverity.WARNING,
                message=rule["message"],
                details=rule["details"],
                suggested_fix=rule["suggested_fix"],
            ))

    em_code = str(payload.get("coding_output", {}).get("em_code", "")).strip()
    procedures_documented = {
        item.strip().lower()
        for item in payload.get("clinical_context", {}).get("procedures_documented", [])
    }
    if em_code and len(codes - {em_code}) > 0 and "separate evaluation and management service" not in procedures_documented:
        em_entry = _find_code_entry(code_entries, em_code)
        modifiers = {str(mod).strip() for mod in em_entry.get("modifiers", [])}
        if "25" not in modifiers:
            issues.append(CodingIssue(
                category="cci_rules",
                severity=AuditSeverity.WARNING,
                message="E/M service was billed with a same-day procedure without modifier 25.",
                details="A separately identifiable evaluation and management service should be documented when modifier 25 is used.",
                suggested_fix="Add modifier 25 only if the note supports a distinct E/M service; otherwise remove the E/M code.",
            ))


def _diagnosis_matches_transcript(transcript: str, diagnosis: Dict[str, object]) -> bool:
    keywords = diagnosis.get("keywords", [])
    if not keywords:
        return True
    lowered = transcript.lower()
    return all(str(keyword).lower() in lowered for keyword in keywords)


def _audit_icd10(payload: Dict[str, object], issues: List[CodingIssue]) -> None:
    transcript = str(payload.get("transcript", ""))
    diagnoses_documented = payload.get("clinical_context", {}).get("diagnoses_documented", [])
    assigned_codes = {
        str(entry.get("code", "")).strip(): entry
        for entry in payload.get("coding_output", {}).get("icd10_codes", [])
        if entry.get("code")
    }

    for diagnosis in diagnoses_documented:
        if not _diagnosis_matches_transcript(transcript, diagnosis):
            continue

        expected_codes = [str(code).strip() for code in diagnosis.get("expected_icd10", []) if str(code).strip()]
        if not expected_codes:
            continue

        expected_present = [code for code in expected_codes if code in assigned_codes]
        if expected_present:
            continue

        label = str(diagnosis.get("label", "documented diagnosis"))
        matching_unspecified = [
            code for code in assigned_codes
            if code.split(".")[0] == expected_codes[0].split(".")[0] or code.endswith(".9")
        ]
        issues.append(CodingIssue(
            category="icd10_specificity",
            severity=AuditSeverity.ERROR,
            message=f"Assigned ICD-10 codes do not capture the documented specificity for {label}.",
            details=f"Expected one of: {', '.join(expected_codes)}; found related codes: {', '.join(matching_unspecified) or 'none'}.",
            suggested_fix=f"Replace or supplement with {', '.join(expected_codes)} if documentation supports it.",
        ))

    for code, entry in assigned_codes.items():
        description = str(entry.get("description", "")).lower()
        if code.endswith(".9") or "unspecified" in description:
            issues.append(CodingIssue(
                category="icd10_specificity",
                severity=AuditSeverity.WARNING,
                message=f"ICD-10 code {code} is unspecified.",
                details="Unspecified diagnosis codes are higher risk when the transcript documents laterality, stage, type, or linkage.",
                suggested_fix="Use the most specific diagnosis supported by the note.",
            ))

    lowered = transcript.lower()
    if "stage 3a" in lowered and "N18.31" not in assigned_codes:
        issues.append(CodingIssue(
            category="icd10_accuracy",
            severity=AuditSeverity.ERROR,
            message="Transcript documents CKD stage 3a but N18.31 was not assigned.",
            suggested_fix="Use N18.31 if the final assessment confirms CKD stage 3a.",
        ))
    if "diabetes" in lowered and "chronic kidney disease" in lowered and "E11.22" not in assigned_codes:
        issues.append(CodingIssue(
            category="icd10_accuracy",
            severity=AuditSeverity.ERROR,
            message="Transcript links diabetes with chronic kidney disease without using the combination code E11.22.",
            suggested_fix="Use E11.22 when the clinician documents diabetic chronic kidney disease.",
        ))


def audit_coding(payload: Dict[str, object]) -> CodingAuditResult:
    """Run the coding verification pipeline on a coded visit payload."""

    issues: List[CodingIssue] = []
    recommended_code = _audit_em_level(payload, issues)
    _audit_cci_rules(payload, issues)
    _audit_icd10(payload, issues)

    mdm = payload.get("clinical_context", {}).get("mdm", {})
    supported_mdm_level = None
    if mdm:
        supported_mdm_level = determine_supported_mdm_level(
            problems=str(mdm.get("problems", "straightforward")),
            data=str(mdm.get("data", "straightforward")),
            risk=str(mdm.get("risk", "straightforward")),
        ).label()

    return CodingAuditResult(
        visit_id=str(payload.get("visit_id", "unknown-visit")),
        recommended_em_code=recommended_code,
        assigned_em_code=str(payload.get("coding_output", {}).get("em_code", "")).strip() or None,
        supported_mdm_level=supported_mdm_level,
        issues=issues,
    )
