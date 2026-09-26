import json
import pytest
from sqlalchemy.orm import Session
from backend.app.core.database import SessionLocal
from backend.app.models.models import Finding, Assessment
from backend.app.services.cve_provenance_service import cve_provenance_service
from backend.app.services.risk_service import risk_service
from backend.app.services.report_service import report_service
from backend.app.api.routes.findings import _serialize_finding

@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_task1_priority_score_canonical_scale_everywhere(db_session: Session):
    """
    TASK 1: Verify that priority score 5.92 is represented on the canonical scale 10.0 everywhere:
    - Serialized finding
    - Risk prioritization calculation
    - Report export JSON
    - Report export HTML
    No display multiplication by 10 (e.g., / 100 is forbidden).
    """
    finding = db_session.query(Finding).filter(Finding.id == "WM-API-DOCS-A018").first()
    assert finding is not None, "Finding WM-API-DOCS-A018 must exist in database"
    assert finding.priority_score == 5.92, f"Expected 5.92, got {finding.priority_score}"

    # 1. Finding serialization
    serialized = _serialize_finding(finding)
    assert serialized["priority_score"] == 5.92
    assert serialized["priority_scale"] == "10.0"
    assert serialized["priority_score_formatted"] == "5.92 / 10.0"

    # 2. Risk service prioritization
    risk_res = risk_service.calculate_finding_priority(finding, "Testing Environment")
    assert risk_res["priority_score"] == 5.92
    assert risk_res["priority_scale"] == "10.0"
    assert risk_res["priority_score_formatted"] == "5.92 / 10.0"
    assert "5.92 / 10.0" in risk_res["explanation"]["summary_statement"]

    # 3. Report JSON
    if finding.assessment_id:
        report_data = report_service.generate_report_data(db_session, finding.assessment_id)
        f_in_report = next((f for f in report_data["findings_detail"] if f["id"] == "WM-API-DOCS-A018"), None)
        assert f_in_report is not None
        assert f_in_report["priority_score"] == 5.92
        assert f_in_report["priority_scale"] == "10.0"
        assert f_in_report["priority_score_formatted"] == "5.92 / 10.0"

        # 4. Report HTML
        html_report = report_service.generate_html_report(db_session, finding.assessment_id)
        assert "Priority: 5.92 / 10.0" in html_report
        assert "/ 100" not in html_report

def test_task2_finding_with_no_verified_cve_never_receives_nvd_score(db_session: Session):
    """
    TASK 2: Verify that WM-API-DOCS-A018 (which has no verified CVE) displays:
    - CVE: Not identified
    - NVD CVSS: Not available
    - Never receives a fabricated NVD CVSS score (like 0.6 / 10.0).
    """
    finding = db_session.query(Finding).filter(Finding.id == "WM-API-DOCS-A018").first()
    assert finding is not None

    prov = cve_provenance_service.get_provenance_for_finding(finding)
    assert prov["cve_id"] is None
    assert prov["cve_status"] == "Not identified"
    assert prov["nvd_cvss"] is None
    assert prov["nvd_cvss_display"] == "Not available"
    assert prov["provenance_verified"] is False

    # Check serialized route output
    serialized = _serialize_finding(finding)
    assert serialized["cve_id"] is None
    assert serialized["cve_status"] == "Not identified"
    assert serialized["nvd_cvss"] is None
    assert serialized["nvd_cvss_display"] == "Not available"

def test_task3_unrelated_cve_cannot_be_attached_to_wm_api_docs(db_session: Session):
    """
    TASK 3: Verify provenance engine rejects attaching unrelated CVE records
    (e.g., OpenSSH CVE-2024-6387, XZ CVE-2024-3094, HTTP/2 CVE-2023-44487)
    to WM-API-DOCS-A018.
    """
    unrelated_cves = [
        {"cve": "CVE-2024-6387", "cvss": 8.1, "ref": "https://nvd.nist.gov/vuln/detail/CVE-2024-6387"},
        {"cve": "CVE-2024-3094", "cvss": 10.0, "ref": "https://nvd.nist.gov/vuln/detail/CVE-2024-3094"},
        {"cve": "CVE-2023-44487", "cvss": 7.5, "ref": "https://nvd.nist.gov/vuln/detail/CVE-2023-44487"},
    ]

    for un_cve in unrelated_cves:
        prov = cve_provenance_service.evaluate_provenance(
            finding_id="WM-API-DOCS-A018",
            category="API Security & Schema Architecture",
            affected_component="Interactive API Documentation (/openapi.json)",
            candidate_cve=un_cve["cve"],
            candidate_cvss=un_cve["cvss"],
            candidate_reference=un_cve["ref"],
            verified_match=True
        )
        assert prov["cve_id"] is None, f"Unrelated CVE {un_cve['cve']} must not be attached to WM-API-DOCS-A018"
        assert prov["cve_status"] == "Not identified"
        assert prov["nvd_cvss"] is None
        assert prov["nvd_cvss_display"] == "Not available"
        assert prov["provenance_verified"] is False

def test_task3_provenance_requires_all_four_criteria():
    """
    TASK 3: Verify that an NVD CVSS score is only confirmed if all 4 criteria are present:
    1. CVE ID
    2. NVD source/reference
    3. Matching affected product/version context
    4. Verified relationship to the finding
    """
    # Missing reference
    p1 = cve_provenance_service.evaluate_provenance(
        finding_id="KAV-SOFT-001",
        category="Software Inventory",
        affected_component="Python 3.10.1",
        candidate_cve="CVE-2023-40217",
        candidate_cvss=7.5,
        candidate_reference=None,
        verified_match=True
    )
    assert p1["provenance_verified"] is False
    assert p1["nvd_cvss"] is None

    # Unverified match
    p2 = cve_provenance_service.evaluate_provenance(
        finding_id="KAV-SOFT-001",
        category="Software Inventory",
        affected_component="Python 3.10.1",
        candidate_cve="CVE-2023-40217",
        candidate_cvss=7.5,
        candidate_reference="https://nvd.nist.gov/vuln/detail/CVE-2023-40217",
        verified_match=False
    )
    assert p2["provenance_verified"] is False

    # Valid confirmed match with all 4 criteria
    p3 = cve_provenance_service.evaluate_provenance(
        finding_id="KAV-SOFT-001",
        category="Software Inventory",
        affected_component="Python 3.10.1",
        candidate_cve="CVE-2023-40217",
        candidate_cvss=7.5,
        candidate_reference="https://nvd.nist.gov/vuln/detail/CVE-2023-40217",
        verified_match=True
    )
    assert p3["provenance_verified"] is True
    assert p3["cve_id"] == "CVE-2023-40217"
    assert p3["nvd_cvss"] == 7.5
    assert p3["nvd_cvss_display"] == "7.5 / 10.0"

def test_task4_version_verification_required_preserved_only_for_real_cve_relationship():
    """
    TASK 4: Preserve 'Version Verification Required' ONLY when an actual candidate CVE/version relationship exists,
    not for findings without CVEs.
    """
    # For a software finding with candidate CVE needing version check:
    p_soft = cve_provenance_service.evaluate_provenance(
        finding_id="KAV-SOFT-002",
        category="Installed Software",
        affected_component="Node.js",
        candidate_cve="CVE-2023-32002",
        candidate_cvss=6.5,
        candidate_reference="https://nvd.nist.gov/vuln/detail/CVE-2023-32002",
        candidate_version_status="VERSION VERIFICATION REQUIRED",
        verified_match=False
    )
    assert p_soft["cve_id"] == "CVE-2023-32002"
    assert p_soft["cve_status"] == "Version Verification Required"
    # Even with Version Verification Required, unverified NVD CVSS is NOT asserted as confirmed
    assert p_soft["nvd_cvss"] is None
    assert p_soft["nvd_cvss_display"] == "Not available"

    # For WM-API-DOCS-A018:
    p_wm = cve_provenance_service.evaluate_provenance(
        finding_id="WM-API-DOCS-A018",
        candidate_version_status="VERSION VERIFICATION REQUIRED"
    )
    assert p_wm["cve_id"] is None
    assert p_wm["cve_status"] == "Not identified"
    assert p_wm["nvd_cvss"] is None
    assert p_wm["nvd_cvss_display"] == "Not available"

def test_task4_json_and_ui_consistency(db_session: Session):
    """
    TASK 4: Verify that report JSON, serialized finding API, and risk prioritization API
    all return matching risk scale ('10.0') and identical CVE/NVD states for WM-API-DOCS-A018.
    """
    finding = db_session.query(Finding).filter(Finding.id == "WM-API-DOCS-A018").first()
    assert finding is not None

    # Serialized Finding API
    serialized = _serialize_finding(finding)

    # Risk Prioritization Item
    prio_list = risk_service.prioritize_all_findings(db_session, finding.assessment_id)
    prio_item = next((p for p in prio_list if p["finding_id"] == "WM-API-DOCS-A018"), None)
    assert prio_item is not None

    # Report Data JSON
    report_data = report_service.generate_report_data(db_session, finding.assessment_id)
    report_item = next((r for r in report_data["findings_detail"] if r["id"] == "WM-API-DOCS-A018"), None)
    assert report_item is not None

    # Verify matching scale
    assert serialized["priority_scale"] == "10.0"
    assert prio_item["priority_scale"] == "10.0"
    assert report_item["priority_scale"] == "10.0"

    # Verify matching scores
    assert serialized["priority_score"] == 5.92
    assert prio_item["priority_score"] == 5.92
    assert report_item["priority_score"] == 5.92

    # Verify matching CVE states
    assert serialized["cve_id"] is None
    assert prio_item["cve_id"] is None
    assert report_item["cve_id"] is None

    assert serialized["cve_status"] == "Not identified"
    assert prio_item["cve_status"] == "Not identified"
    assert report_item["cve_status"] == "Not identified"

    # Verify matching NVD CVSS states
    assert serialized["nvd_cvss"] is None
    assert prio_item["nvd_cvss"] is None
    assert report_item["nvd_cvss"] is None

    assert serialized["nvd_cvss_display"] == "Not available"
    assert prio_item["nvd_cvss_display"] == "Not available"
    assert report_item["nvd_cvss_display"] == "Not available"
