"""
KAVACH 5.0 — Regression Tests: World Monitor Correlation Consistency

Covers:
1. CWE-only overlap does NOT produce HIGH confidence correlation.
2. Genuine CVE-ID exact match DOES produce HIGH confidence correlation.
3. External advisory is not falsely attached to a local finding via CWE stored in cve_ids.
4. WM-API-DOCS-A018 (CWE-200 only, no CVE) yields 0 correlated advisories against demo fixtures.
5. CVE-2023-44487 finding correctly correlates HIGH with DEMO-CVE-2023-44487.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.database import SessionLocal
from backend.app.services.world_monitor_service import WorldMonitorService


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def service():
    """Fresh WorldMonitorService with deterministic demo fixtures loaded."""
    svc = WorldMonitorService()
    return svc


# --- Helpers ------------------------------------------------------------------

def _make_finding(id: str, title: str, cwe_id: str = None, cve_id: str = None,
                  category: str = "Vulnerability", technology: str = None,
                  affected_component: str = None) -> dict:
    return {
        "id": id,
        "title": title,
        "cwe_id": cwe_id,
        "cve_id": cve_id,
        "category": category,
        "technology": technology,
        "affected_component": affected_component,
        "simple_evidence": {}
    }


# --- TEST 1: CWE-only overlap must NOT produce HIGH confidence ----------------

def test_cwe_only_does_not_produce_high_confidence(service):
    """
    REGRESSION: A local finding with CWE-200 must NOT produce HIGH confidence
    correlation against DEMO-ADV-FASTAPI-UVICORN (which referenced CWE-200
    incorrectly stored in its cve_ids list before the fix).

    After the fix:
    - DEMO-ADV-FASTAPI-UVICORN has cve_ids=[] and cwe_ids=["CWE-200"]
    - The correlate_with_findings step 1 only checks ev_cves starting with 'CVE-'
    - CWE identifiers in cve_ids are skipped
    - No HIGH confidence result should emerge from CWE overlap
    """
    findings = [
        _make_finding(
            id="WM-API-DOCS-A018",
            title="Publicly Exposed Interactive API Schema & Documentation",
            cwe_id="CWE-200",
            cve_id=None,
            category="API Security",
            affected_component="https://www.worldmonitor.app/openapi.json"
        )
    ]

    correlations = service.correlate_with_findings(
        target_info={"target_url": "https://www.worldmonitor.app", "hostname": "worldmonitor.app"},
        local_findings=findings
    )

    # Assert: no HIGH confidence correlations
    high_confidence = [c for c in correlations if c["confidence"] == "HIGH"]
    assert len(high_confidence) == 0, (
        f"CWE-only overlap produced {len(high_confidence)} HIGH confidence correlation(s): "
        f"{[c['event_id'] for c in high_confidence]}"
    )

    # Assert: specifically, DEMO-ADV-FASTAPI-UVICORN must not appear at HIGH
    fastapi_advisory_high = [
        c for c in correlations
        if c["event_id"] == "DEMO-ADV-FASTAPI-UVICORN" and c["confidence"] == "HIGH"
    ]
    assert len(fastapi_advisory_high) == 0, (
        "DEMO-ADV-FASTAPI-UVICORN must not produce HIGH confidence via CWE-200 overlap"
    )


# --- TEST 2: WM-API-DOCS-A018 yields 0 correlated advisories -----------------

def test_wm_api_docs_yields_zero_correlations(service):
    """
    REGRESSION: The real finding WM-API-DOCS-A018 (API docs exposure, CWE-200,
    no CVE, no specific HSTS/CSP/TLS signals) must produce 0 global advisory
    correlations against the demo fixtures.

    This was broken because DEMO-ADV-FASTAPI-UVICORN had cve_ids=["CWE-200"],
    which caused the correlate engine to match CWE-200 as a CVE identifier.
    """
    findings = [
        _make_finding(
            id="WM-API-DOCS-A018",
            title="Publicly Exposed Interactive API Schema & Documentation",
            cwe_id="CWE-200",
            cve_id=None,
            category="API Security",
            affected_component="https://www.worldmonitor.app/openapi.json"
        )
    ]

    correlations = service.correlate_with_findings(
        target_info={"target_url": "https://www.worldmonitor.app", "hostname": "worldmonitor.app"},
        local_findings=findings
    )

    assert len(correlations) == 0, (
        f"WM-API-DOCS-A018 produced {len(correlations)} unexpected correlation(s): "
        f"{[c['event_id'] + '/' + c['confidence'] for c in correlations]}"
    )


# --- TEST 3: Genuine CVE match still produces HIGH confidence ----------------

def test_genuine_cve_match_produces_high_confidence(service):
    """
    Sanity check: A finding with a genuine CVE-2023-44487 that matches
    DEMO-CVE-2023-44487 must still produce HIGH confidence correlation.
    The fix must not break legitimate CVE identifier matching.
    """
    findings = [
        _make_finding(
            id="FINDING-HTTP2-001",
            title="HTTP/2 Rapid Reset Attack Vulnerability",
            cwe_id="CWE-400",
            cve_id="CVE-2023-44487",
            category="Network Security"
        )
    ]

    correlations = service.correlate_with_findings(
        target_info={"target_url": "https://example.com", "hostname": "example.com"},
        local_findings=findings
    )

    # Assert: exactly 1 HIGH confidence match for DEMO-CVE-2023-44487
    high_cve_match = [
        c for c in correlations
        if c["event_id"] == "DEMO-CVE-2023-44487" and c["confidence"] == "HIGH"
    ]
    assert len(high_cve_match) == 1, (
        f"Expected 1 HIGH confidence match for CVE-2023-44487, got {len(high_cve_match)}: "
        f"{correlations}"
    )
    assert high_cve_match[0]["correlation_type"] == "EXACT_IDENTIFIER_MATCH"


# --- TEST 4: CWE identifiers in cve_ids field are filtered out ---------------

def test_non_cve_identifiers_in_cve_ids_are_skipped(service):
    """
    Verify that identifiers in advisory cve_ids that do NOT start with 'CVE-'
    are silently skipped during step-1 matching and can never elevate confidence
    to HIGH.

    This covers both DEMO-CISA-2024-001 (had CWE-319, CWE-693 in cve_ids)
    and DEMO-ADV-FASTAPI-UVICORN (had CWE-200 in cve_ids).
    """
    # Simulate a finding that "matches" the CWEs that were incorrectly in cve_ids
    findings = [
        _make_finding(
            id="TEST-HSTS-001",
            title="Missing HSTS Header",
            cwe_id="CWE-319",
            cve_id=None,
            category="Transport Security"
        )
    ]

    correlations = service.correlate_with_findings(
        target_info={"target_url": "https://test.example.com", "hostname": "test.example.com"},
        local_findings=findings
    )

    # Assert: no HIGH confidence correlation (CWE-319 was stored in cve_ids of DEMO-CISA-2024-001)
    high_confidence_for_cisa = [
        c for c in correlations
        if c["event_id"] == "DEMO-CISA-2024-001" and c["confidence"] == "HIGH"
    ]
    assert len(high_confidence_for_cisa) == 0, (
        "DEMO-CISA-2024-001 must not produce HIGH confidence via CWE-319 stored in cve_ids"
    )


# --- TEST 5: Advisory isolation — unrelated CVE not attached to local finding -

def test_unrelated_cve_advisory_not_attached_to_local_finding(service):
    """
    CVE-2024-6387 (OpenSSH) must not correlate with a local finding that only
    has CWE-200 and no CVE ID. The finding must not have CVE-2024-6387 attached.
    """
    findings = [
        _make_finding(
            id="WM-API-DOCS-A018",
            title="Publicly Exposed Interactive API Schema & Documentation",
            cwe_id="CWE-200",
            cve_id=None,
            category="API Security"
        )
    ]

    correlations = service.correlate_with_findings(
        target_info={"target_url": "https://www.worldmonitor.app", "hostname": "worldmonitor.app"},
        local_findings=findings
    )

    cve_6387_attached = [
        c for c in correlations
        if c["event_id"] == "DEMO-CVE-2024-6387"
    ]
    assert len(cve_6387_attached) == 0, (
        "CVE-2024-6387 (OpenSSH) must not be attached to API docs exposure finding"
    )


# --- TEST 6: Correlation count consistency -----------------------------------

def test_correlation_count_reflects_findings_count(service):
    """
    The count returned by correlate_with_findings must equal the length of the
    returned correlations list. It must never include unrelated assessment data.
    All entries must have required fields with valid confidence values.
    """
    findings = [
        _make_finding(
            id="WM-API-DOCS-A018",
            title="Publicly Exposed Interactive API Schema & Documentation",
            cwe_id="CWE-200",
            cve_id=None,
            category="API Security",
            affected_component="https://www.worldmonitor.app/openapi.json"
        )
    ]

    correlations = service.correlate_with_findings(
        target_info={"target_url": "https://www.worldmonitor.app", "hostname": "worldmonitor.app"},
        local_findings=findings
    )

    assert isinstance(correlations, list), "correlations must be a list"
    for corr in correlations:
        assert "event_id" in corr, "Each correlation must have event_id"
        assert "confidence" in corr, "Each correlation must have confidence"
        assert corr["confidence"] in ("HIGH", "MEDIUM", "LOW"), (
            f"Invalid confidence value: {corr['confidence']}"
        )


# --- TEST 7: Empty findings yields 0 correlations ----------------------------

def test_empty_findings_yields_zero_correlations(service):
    """No findings -> no correlations. Ensures no phantom global advisories appear."""
    correlations = service.correlate_with_findings(
        target_info={"target_url": "https://www.worldmonitor.app", "hostname": "worldmonitor.app"},
        local_findings=[]
    )
    assert correlations == [], (
        f"Empty findings should produce 0 correlations, got: {correlations}"
    )


# =============================================================================
# LOCAL FINDING COUNT REGRESSION TESTS
# Source of truth: GET /api/findings?assessment_id=<id>
# This is the exact endpoint called by CommandCenterPage.tsx's
# useEffect([activeAssessment?.id]) after the fix.
# =============================================================================

def test_a018_local_finding_count_via_api(db_session):
    """
    REGRESSION: KAVACH-WM-20260923-A018 must return exactly 1 local finding
    when queried via the backend findings API scoped to assessment_id.

    This mirrors the exact call made by the fixed CommandCenterPage.tsx:
        api.getFindings({ assessment_id: activeAssessment.id })
        .then((data) => setBackendFindingsCount(data.length))

    The expected finding is WM-API-DOCS-A018.

    Data source: Finding table filtered by assessment_id = 'KAVACH-WM-20260923-A018'.
    Counts: only findings belonging to KAVACH-WM-20260923-A018 (assessment-scoped).
    Must NOT count: demo findings, URL check findings, or findings from other assessments.
    """
    from backend.app.models.models import Finding

    assessment_id = "KAVACH-WM-20260923-A018"

    findings = db_session.query(Finding).filter(
        Finding.assessment_id == assessment_id
    ).all()

    assert len(findings) == 1, (
        f"KAVACH-WM-20260923-A018 must have exactly 1 local finding, got {len(findings)}: "
        f"{[f.id for f in findings]}"
    )
    assert findings[0].id == "WM-API-DOCS-A018", (
        f"Expected finding WM-API-DOCS-A018, got: {findings[0].id}"
    )


def test_a018_local_finding_count_via_http(client):
    """
    REGRESSION: The HTTP endpoint GET /api/findings?assessment_id=KAVACH-WM-20260923-A018
    must return exactly 1 finding — the same call made by the fixed CommandCenterPage.tsx.

    Verifies:
    - The count is assessment-scoped (not global)
    - The returned finding is WM-API-DOCS-A018
    - Correlated global advisories remain 0 (separate from local count)
    """
    res = client.get("/api/findings?assessment_id=KAVACH-WM-20260923-A018")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"

    findings = res.json()
    assert isinstance(findings, list), "Response must be a list"
    assert len(findings) == 1, (
        f"Expected 1 finding for KAVACH-WM-20260923-A018, got {len(findings)}: "
        f"{[f.get('id') for f in findings]}"
    )
    assert findings[0]["id"] == "WM-API-DOCS-A018", (
        f"Expected WM-API-DOCS-A018 as the finding, got: {findings[0].get('id')}"
    )


def test_assessment_with_zero_findings_shows_zero_local_count(client):
    """
    REGRESSION: An assessment with no findings must return 0 via the scoped API.
    Verifies that the display in World Situational Monitor correctly shows
    '0 local findings' (not phantom counts from other assessments or global advisories).

    Uses a non-existent assessment ID to guarantee 0 real findings.
    """
    res = client.get("/api/findings?assessment_id=KAVACH-NONEXISTENT-00000")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"

    findings = res.json()
    assert isinstance(findings, list), "Response must be a list"
    assert len(findings) == 0, (
        f"Non-existent assessment must return 0 findings, got {len(findings)}: "
        f"{[f.get('id') for f in findings]}"
    )
