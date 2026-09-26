"""
Unit tests for KAVACH Local Ollama AI Explanation Engine Integration:
- Centralized config (AI/config.json)
- Sensitive credential & secret data masking
- 4-state lifecycle status reporting
- 6 AI Explanation Functions with 7 structured sections
- 100% deterministic rule fallback when AI is offline
"""

from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.ollama_service import ollama_service
from backend.app.core.config import settings

client = TestClient(app)

def test_centralized_ai_config_loaded():
    """Verify that configuration from AI/config.json was properly loaded."""
    assert settings.OLLAMA_MODEL in ("llama3", "phi3")
    assert "11434" in settings.OLLAMA_BASE_URL
    assert settings.AI_MASK_SENSITIVE is True

def test_sensitive_data_masking():
    """Verify regex-based sanitization of credentials, keys, and tokens."""
    raw_sample = (
        "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE "
        "DATABASE_URL=postgresql://admin:super_secret_password_123@localhost:5432/kavach "
        "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.doNotLeakThisSignature "
        "SLACK_HOOK=https://hooks.slack.com/services/T00/B00/SECRETTOKEN123"
    )
    masked = ollama_service.mask_sensitive_data(raw_sample)

    assert "AKIAIOSFODNN7EXAMPLE" not in masked
    assert "AKIA***[MASKED_AWS_KEY]" in masked

    assert "super_secret_password_123" not in masked
    assert "***[MASKED_PASSWORD]" in masked

    assert "doNotLeakThisSignature" not in masked
    assert "***[MASKED_BEARER_TOKEN]" in masked

    assert "SECRETTOKEN123" not in masked
    assert "***[MASKED_WEBHOOK]" in masked

def test_ai_status_endpoint_4_states():
    """Verify that /api/ai/status returns valid 4-state lifecycle schema."""
    res = client.get("/api/ai/status")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["lifecycle_state"] in ("AI READY", "AI STARTING", "MODEL UNAVAILABLE", "AI OFFLINE")
    assert data["status_dot"] in ("🟢", "🟡", "🟠", "🔴")
    assert "endpoint" in data
    assert "selected_model" in data

def test_explain_finding_structured_7_sections():
    """Verify AI Function 1 produces the mandatory 7-section structured output."""
    # Fetch first finding
    findings_res = client.get("/api/findings?is_demo=true")
    assert findings_res.status_code == 200
    findings = findings_res.json()
    assert len(findings) > 0
    test_finding_id = findings[0]["id"]

    res = client.post("/api/ai/explain-finding", json={"finding_id": test_finding_id})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["finding_id"] == test_finding_id
    exp = data["explanation"]

    # Verify exact 7 keys
    mandatory_keys = [
        "what_was_found",
        "where",
        "why_it_matters",
        "possible_impact",
        "recommended_action",
        "how_to_fix",
        "how_to_verify"
    ]
    for k in mandatory_keys:
        assert k in exp, f"Missing mandatory section key: {k}"
        assert len(str(exp[k])) > 0

    assert exp["ai_mode"] in ("OLLAMA_LLM", "OLLAMA_RAG", "DETERMINISTIC_RULE_FALLBACK")

def test_explain_risk_function():
    """Verify AI Function 2: Risk Explanation."""
    findings_res = client.get("/api/findings?is_demo=true")
    test_finding_id = findings_res.json()[0]["id"]

    res = client.post("/api/ai/explain-risk", json={"finding_id": test_finding_id})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    risk = data["risk_explanation"]
    assert "reason_for_severity" in risk
    assert "possible_impact" in risk
    assert "why_it_matters" in risk

def test_remediation_guide_function():
    """Verify AI Function 3: Remediation Guide."""
    findings_res = client.get("/api/findings?is_demo=true")
    test_finding_id = findings_res.json()[0]["id"]

    res = client.post("/api/ai/remediation-guide", json={"finding_id": test_finding_id})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    guide = data["remediation_guide"]
    assert "recommended_action" in guide
    assert "how_to_fix" in guide
    assert "how_to_verify" in guide

def test_threat_alert_explanation():
    """Verify AI Function 6: Threat Alert Explanation."""
    res = client.post("/api/ai/threat-alert", json={
        "alert_text": "Anomalous rate of 401 Unauthorized responses with rotating Authorization tokens detected.",
        "component": "API Gateway / Auth Controller",
        "severity": "HIGH"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    alert_exp = data["alert_explanation"]
    assert "what_was_found" in alert_exp
    assert "why_it_matters" in alert_exp
    assert "how_to_fix" in alert_exp
    assert "how_to_verify" in alert_exp
