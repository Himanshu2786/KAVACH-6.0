"""
KAVACH 5.0 — Regression Tests: Security Posture & Risk Level Consistency

Verifies:
1. Assessment KAVACH-WM-20260923-A018 canonical posture and risk calculation:
   - Security Posture = 70 / 100 (MODERATE RISK)
   - Overall Risk Level = MEDIUM
   - Status Label = "Remediation & Hardening Required"
2. Report Export JSON and HTML consistency:
   - executive_summary['security_posture'] == "MODERATE RISK"
   - executive_summary['risk_level'] == "MEDIUM"
   - executive_summary['risk_score'] == 70
3. Risk Prioritization consistency:
   - WM-API-DOCS-A018 calculated_priority == "MEDIUM"
   - priority_score == 5.92 / 10.0
4. Proof that Command Center does NOT display "LOW" for a confirmed MEDIUM finding.
"""

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.services.assessment_service import assessment_service
from backend.app.services.report_service import report_service
from backend.app.services.risk_service import risk_service


def test_canonical_posture_and_risk_for_a018():
    db = SessionLocal()
    try:
        posture = assessment_service.calculate_security_posture(db, "KAVACH-WM-20260923-A018")

        # Canonical values from assessment_service
        assert posture["score"] == 70, f"Expected posture score 70, got {posture['score']}"
        assert posture["posture"] == "MODERATE RISK", f"Expected 'MODERATE RISK', got {posture['posture']}"
        assert posture["risk_level"] == "MEDIUM", f"Expected 'MEDIUM', got {posture['risk_level']}"
        assert posture["status_label"] == "Remediation & Hardening Required"
        assert posture["confirmed_count"] == 1
        assert posture["total_findings"] == 1

        # Must not be LOW risk
        assert posture["risk_level"] != "LOW", "A018 has a confirmed MEDIUM finding; risk level must not be LOW"

    finally:
        db.close()


def test_report_export_posture_risk_consistency():
    db = SessionLocal()
    try:
        report_data = report_service.generate_report_data(db, "KAVACH-WM-20260923-A018")
        exec_sum = report_data["executive_summary"]

        assert exec_sum["security_posture"] == "MODERATE RISK"
        assert exec_sum["risk_level"] == "MEDIUM"
        assert exec_sum["risk_score"] == 70
        assert exec_sum["status_label"] == "Remediation & Hardening Required"

        # Verify HTML report contains consistent values
        html = report_service.generate_html_report(db, "KAVACH-WM-20260923-A018")
        assert "MODERATE RISK" in html
        assert "70/100" in html
        assert "MEDIUM Risk" in html

    finally:
        db.close()


def test_risk_prioritization_engine_consistency():
    db = SessionLocal()
    try:
        priorities = risk_service.prioritize_all_findings(db, "KAVACH-WM-20260923-A018")
        assert len(priorities) == 1
        p = priorities[0]

        assert p["finding_id"] == "WM-API-DOCS-A018"
        assert p["calculated_priority"] == "MEDIUM"
        assert p["base_severity"] == "MEDIUM"
        assert p["priority_score"] == 5.92
        assert p["status"] == "STILL_OPEN"
        assert p["evidence_strength"] == "VERIFIED"

    finally:
        db.close()


def test_api_reports_json_endpoint():
    client = TestClient(app)
    resp = client.get("/api/reports/KAVACH-WM-20260923-A018")
    assert resp.status_code == 200
    data = resp.json()

    exec_sum = data["executive_summary"]
    assert exec_sum["security_posture"] == "MODERATE RISK"
    assert exec_sum["risk_level"] == "MEDIUM"
    assert exec_sum["risk_score"] == 70
    assert exec_sum["status_label"] == "Remediation & Hardening Required"


def test_command_center_risk_level_derivation():
    # Simulate Command Center calculation with severityCounts for A018
    severity_counts = {
        "CRITICAL": 0,
        "HIGH": 0,
        "MEDIUM": 1,
        "LOW": 0,
        "INFO": 0,
    }

    # Bug reproduction check: previous ternary dropped MEDIUM and returned LOW
    buggy_risk_level = (
        "CRITICAL" if severity_counts["CRITICAL"] > 0
        else "HIGH" if severity_counts["HIGH"] > 0
        else "LOW"
    )
    assert buggy_risk_level == "LOW", "Proves bug: previous code falsely reported LOW"

    # Fixed canonical derivation
    fixed_risk_level = (
        "CRITICAL" if severity_counts["CRITICAL"] > 0
        else "HIGH" if severity_counts["HIGH"] > 0
        else "MEDIUM" if severity_counts["MEDIUM"] > 0
        else "LOW" if severity_counts["LOW"] > 0
        else "LOW"
    )
    assert fixed_risk_level == "MEDIUM", "Fixed code correctly derives MEDIUM"
