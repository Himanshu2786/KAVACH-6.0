"""
Unit Tests for KAVACH 5.0 — Priority 7: Ollama as Evidence Analyst.

Validates:
1. Strict Truth Hierarchy:
   REAL OBSERVATION > REAL SOURCE CODE > REAL TOOL OUTPUT > DETERMINISTIC DETECTION > AI INTERPRETATION
2. Real-only input grounding & sensitive data masking.
3. 5-point output structure:
   - simple explanation
   - technical explanation
   - impact explanation
   - remediation explanation
   - judge-friendly explanation
4. Strict "Insufficient evidence." guard when evidence is missing or ungrounded.
5. Deterministic fallback continuity when Ollama is offline.
6. Provenance labeling ("AI-ASSISTED" vs "DETERMINISTIC").
7. Attribution integrity: Detector discovered the vulnerability, AI/Deterministic analyzed it.
8. API Route /api/ai/explain-5-points.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.ai_analysis_service import (
    AIAnalysisService,
    ai_analysis_service,
    TRUTH_HIERARCHY as BACKEND_TRUTH_HIERARCHY
)
from services.ollama_service import (
    OllamaService,
    ollama_service as desktop_ollama_service,
    TRUTH_HIERARCHY as DESKTOP_TRUTH_HIERARCHY
)
from backend.app.core.database import get_db, Base, engine, SessionLocal
from backend.app.models.models import Finding, EvidenceRecord, Assessment


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Create test assessment
    assessment = Assessment(
        id="test-p7-assessment-01",
        name="Production API Gateway",
        target_url="https://api.test.gov/v1",
        status="COMPLETED"
    )
    db.merge(assessment)

    # Finding 1: Confirmed with real evidence
    finding_confirmed = Finding(
        id="test-p7-finding-sql-01",
        assessment_id="test-p7-assessment-01",
        title="SQL Injection in /api/v1/users",
        description="Deterministic AST analyzer detected unsanitized input passed to raw SQL query.",
        base_severity="CRITICAL",
        category="SQL Injection",
        status="CONFIRMED",
        cwe_id="CWE-89",
        priority_score=9.8
    )
    db.merge(finding_confirmed)

    evidence_sql = EvidenceRecord(
        id="test-p7-ev-01",
        finding_id="test-p7-finding-sql-01",
        evidence_type="HTTP_INTERACTION",
        description="Observed SQL parameter reflection and database error on ID payload.",
        raw_data="GET /api/v1/users?id=1%27%20OR%201=1-- HTTP/1.1\nHost: api.test.gov\nResponse: 200 OK [{\"id\": 1, \"name\": \"admin\"}]",
        where_found="/backend/app/routes/users.py:42",
        observed_output="200 OK with admin object leak",
        validation_result="CONFIRMED",
        evidence_nature="REAL EVIDENCE"
    )
    db.merge(evidence_sql)

    # Finding 2: Unconfirmed / No evidence (should trigger "Insufficient evidence.")
    finding_unconfirmed = Finding(
        id="test-p7-finding-unconf-02",
        assessment_id="test-p7-assessment-01",
        title="Potential Hardcoded Secret",
        description="Heuristic flag with no verified secret value.",
        base_severity="LOW",
        category="Hardcoded Secret",
        status="NOT CONFIRMED",
        cwe_id="CWE-798"
    )
    db.merge(finding_unconfirmed)

    db.commit()
    yield db
    db.close()


def test_truth_hierarchy_definition():
    """Verify the strict Truth Hierarchy is accurately defined across backend and desktop services."""
    expected = [
        "REAL_OBSERVATION",
        "REAL_SOURCE_CODE",
        "REAL_TOOL_OUTPUT",
        "DETERMINISTIC_DETECTION",
        "AI_INTERPRETATION"
    ]
    assert BACKEND_TRUTH_HIERARCHY == expected
    assert DESKTOP_TRUTH_HIERARCHY == expected
    # AI INTERPRETATION must be at the very bottom (lowest priority)
    assert BACKEND_TRUTH_HIERARCHY[-1] == "AI_INTERPRETATION"
    assert BACKEND_TRUTH_HIERARCHY[0] == "REAL_OBSERVATION"


def test_deterministic_5_point_fallback_structure(setup_db):
    """Verify deterministic fallback produces all 5 explanation dimensions with DETERMINISTIC provenance."""
    db = setup_db
    finding = db.query(Finding).filter(Finding.id == "test-p7-finding-sql-01").first()
    evidence = finding.evidence_records[0]

    service = AIAnalysisService()
    fallback = service._generate_structured_rule_fallback(finding, evidence)

    # Check 5 explanation keys
    assert "simple_explanation" in fallback
    assert "technical_explanation" in fallback
    assert "impact_explanation" in fallback
    assert "remediation_explanation" in fallback
    assert "judge_friendly_explanation" in fallback

    # Check provenance and attribution
    assert fallback["provenance"] == "DETERMINISTIC"
    assert fallback["discovered_by"] in ["DETERMINISTIC_DETECTOR", "Detector/Security Engine", "CWE-89"]
    assert "AI" not in fallback["discovered_by"]
    assert fallback["truth_hierarchy"] == BACKEND_TRUTH_HIERARCHY



def test_insufficient_evidence_guard_on_unconfirmed_finding(setup_db):
    """Verify that when evidence is absent/unconfirmed, AI returns 'Insufficient evidence.'."""
    db = setup_db
    finding = db.query(Finding).filter(Finding.id == "test-p7-finding-unconf-02").first()

    service = AIAnalysisService()
    result = asyncio.run(service.generate_5_point_explanation(finding, None))

    assert result["technical_explanation"] == "Insufficient evidence."
    assert result["provenance"] == "DETERMINISTIC"
    assert "No verifiable technical proof" in result["simple_explanation"] or "Insufficient evidence" in result["simple_explanation"]


def test_desktop_service_insufficient_evidence_guard():
    """Verify desktop OllamaService also returns 'Insufficient evidence.' when evidence is missing."""
    empty_finding = {
        "title": "Unverified Open Port",
        "description": "Port scan was incomplete",
        "status": "NOT CONFIRMED"
    }

    result = desktop_ollama_service.generate_5_point_explanation(empty_finding, None)
    assert result["technical_explanation"] == "Insufficient evidence."
    assert result["provenance"] == "DETERMINISTIC"


def test_ollama_ai_assisted_explanation_mocked():
    """Verify that when Ollama returns valid JSON, output is marked AI-ASSISTED while retaining detector discovery."""
    mock_ai_json_response = """
    {
        "simple_explanation": "The app puts user text directly into database commands without checking it first.",
        "technical_explanation": "Observed SQL query concatenation in users.py line 42 with verified payload response.",
        "impact_explanation": "Attackers can read, modify, or delete database tables and bypass login.",
        "remediation_explanation": "Replace raw SQL string formatting with parameterized queries using SQLAlchemy or cursor parameters.",
        "judge_friendly_explanation": "An open door that allows anyone to issue unauthorized commands straight to the data vault.",
        "confidence": 0.95
    }
    """

    service = AIAnalysisService()
    
    with patch("backend.app.services.ai_analysis_service.ollama_service.check_health", new_callable=AsyncMock) as mock_health, \
         patch("backend.app.services.ai_analysis_service.ollama_service.generate_completion", new_callable=AsyncMock) as mock_comp:
        mock_health.return_value = {"status_code": "ready"}
        mock_comp.return_value = mock_ai_json_response

        finding_dict = {
            "id": "find-101",
            "title": "SQL Injection in /api/v1/users",
            "description": "Detected raw query execution",
            "severity": "CRITICAL",
            "status": "CONFIRMED"
        }
        evidence_dict = {
            "raw_request": "GET /api/v1/users?id=1%27 HTTP/1.1",
            "raw_response": "HTTP/1.1 500 Database Error",
            "code_snippet": "cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')",
            "source_file": "routes/users.py",
            "line_number": 42
        }

        result = asyncio.run(service.generate_5_point_explanation(finding_dict, evidence_dict))

        assert result["provenance"] == "AI-ASSISTED"
        assert result["discovered_by"] == "Detector/Security Engine"
        assert "Ollama" in result["analyzed_by"]
        assert result["simple_explanation"] == "The app puts user text directly into database commands without checking it first."
        assert result["remediation_explanation"].startswith("Replace raw SQL")
        assert result["truth_hierarchy"] == BACKEND_TRUTH_HIERARCHY


def test_sensitive_data_masked_in_ollama_prompt():
    """Verify sensitive tokens and passwords are never sent raw into Ollama prompts."""
    raw_request_with_token = "POST /api/login HTTP/1.1\nAuthorization: Bearer [REDACTED_TOKEN]\nPassword: my_super_secret_password"
    masked = desktop_ollama_service.mask_sensitive_data(raw_request_with_token)

    assert "secret_jwt_token_12345" not in masked
    assert "my_super_secret_password" not in masked
    assert "[MASKED_BEARER_TOKEN]" in masked or "[MASKED_TOKEN]" in masked
    assert "[MASKED]" in masked



def test_api_route_explain_5_points(setup_db):
    """Verify FastAPI endpoint POST /api/ai/explain-5-points."""
    client = TestClient(app)

    response = client.post("/api/ai/explain-5-points", json={"finding_id": "test-p7-finding-sql-01"})
    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["finding_id"] == "test-p7-finding-sql-01"
    
    explanation_data = data["data"]
    assert "simple_explanation" in explanation_data
    assert "technical_explanation" in explanation_data
    assert "impact_explanation" in explanation_data
    assert "remediation_explanation" in explanation_data
    assert "judge_friendly_explanation" in explanation_data
    assert explanation_data["provenance"] in ["AI-ASSISTED", "DETERMINISTIC"]
    assert explanation_data["discovered_by"] == "Detector/Security Engine"
    assert explanation_data["truth_hierarchy"] == BACKEND_TRUTH_HIERARCHY


def test_api_route_explain_5_points_not_found():
    """Verify FastAPI endpoint returns 404 for unknown finding ID."""
    client = TestClient(app)
    response = client.post("/api/ai/explain-5-points", json={"finding_id": "non-existent-finding-id-999"})
    assert response.status_code == 404
