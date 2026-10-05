"""
Unit tests for KAVACH Local Ollama AI Explanation Engine Integration:
- Centralized config (AI/config.json)
- Sensitive credential & secret data masking
- 4-state lifecycle status reporting
- 6 AI Explanation Functions with 7 structured sections
- 100% deterministic rule fallback when AI is offline
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock
import httpx
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


def test_ollama_auth_headers_empty_key(monkeypatch):
    """A. Verify no Authorization header is produced when OLLAMA_API_KEY is empty."""
    monkeypatch.setattr(settings, "OLLAMA_API_KEY", "")
    headers = ollama_service._get_headers()
    assert "Authorization" not in headers


def test_ollama_auth_headers_configured_key(monkeypatch):
    """B. Verify Authorization header is formatted as Bearer <key> when OLLAMA_API_KEY is set."""
    dummy_key = "test_cloud_api_key_sample"
    monkeypatch.setattr(settings, "OLLAMA_API_KEY", dummy_key)
    headers = ollama_service._get_headers()
    assert headers.get("Authorization") == f"Bearer {dummy_key}"


def test_ollama_health_check_mocked_200(monkeypatch):
    """C. Verify health check succeeds and detects models with mocked HTTP 200."""
    async def _run():
        dummy_key = "test_cloud_api_key_sample"
        monkeypatch.setattr(settings, "OLLAMA_API_KEY", dummy_key)
        monkeypatch.setattr(ollama_service, "selected_model", "llama3")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "models": [{"name": "llama3:latest"}, {"name": "phi3:latest"}]
        }

        captured_headers = {}

        async def mock_get(url, *args, **kwargs):
            nonlocal captured_headers
            captured_headers = kwargs.get("headers", {})
            return mock_resp

        with patch("httpx.AsyncClient.get", new=mock_get):
            health = await ollama_service.check_health()
            assert health["status"] == "online"
            assert health["lifecycle_state"] == "AI READY"
            assert health["status_code"] == "ready"
            assert health["status_dot"] == "🟢"
            assert captured_headers.get("Authorization") == f"Bearer {dummy_key}"

    asyncio.run(_run())


def test_ollama_failure_returns_deterministic_fallback(monkeypatch):
    """D. Verify connection failure returns deterministic fallback and AI OFFLINE lifecycle state."""
    async def _run():
        monkeypatch.setattr(settings, "OLLAMA_API_KEY", "")
        with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("Connection refused")):
            health = await ollama_service.check_health()
            assert health["status"] == "offline"
            assert health["lifecycle_state"] == "AI OFFLINE"
            assert health["status_code"] == "offline"
            assert health["status_dot"] == "🔴"
            assert "deterministic rule mode" in health["message"]

    asyncio.run(_run())


def test_api_key_never_exposed_in_status_or_errors(monkeypatch):
    """E. Verify API key is strictly excluded from status payload, messages, and masked from output."""
    async def _run():
        dummy_secret = "super_secret_test_ollama_token_98765"
        monkeypatch.setattr(settings, "OLLAMA_API_KEY", dummy_secret)

        # 1. Check health check status payload
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"models": [{"name": "llama3:latest"}]}

        with patch("httpx.AsyncClient.get", return_value=mock_resp):
            health = await ollama_service.check_health()
            for k, v in health.items():
                assert dummy_secret not in str(v), f"Secret exposed in health field '{k}'"

        # 2. Check offline error response
        with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("Connection refused")):
            offline_health = await ollama_service.check_health()
            for k, v in offline_health.items():
                assert dummy_secret not in str(v), f"Secret exposed in offline field '{k}'"

        # 3. Check sensitive data masking helper
        sample_text = f"Ollama cloud returned auth Bearer {dummy_secret}"
        masked = ollama_service.mask_sensitive_data(sample_text)
        assert dummy_secret not in masked
        assert "[MASKED_BEARER_TOKEN]" in masked

    asyncio.run(_run())


def test_ai_provenance_fallback_when_offline():
    """Verify ai_provider is 'fallback' when Ollama is offline or uncalled."""
    findings_res = client.get("/api/findings?is_demo=true")
    assert findings_res.status_code == 200
    findings = findings_res.json()
    assert len(findings) > 0
    f = findings[0]
    # Finding response includes ai_provider
    assert "ai_provider" in f
    assert f["ai_provider"] in ("ollama", "fallback")

    # Call explain-finding under offline condition (side_effect)
    with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("Connection refused")):
        res = client.post("/api/ai/explain-finding", json={"finding_id": f["id"]})
        assert res.status_code == 200
        data = res.json()
        assert data["ai_provider"] == "fallback"
        assert data["explanation"]["ai_provider"] == "fallback"


def test_ai_provenance_ollama_when_success():
    """Verify ai_provider is 'ollama' when Ollama completion actually succeeds."""
    import json
    findings_res = client.get("/api/findings?is_demo=true")
    f = findings_res.json()[0]

    mock_ollama_res = {
        "what_was_found": "Ollama generated finding summary.",
        "where": "/api/v1/resource",
        "why_it_matters": "Ollama hypothesis.",
        "possible_impact": "High risk impact.",
        "severity_rationale": "Clear rationale.",
        "recommended_action": "Apply patch.",
        "how_to_fix": "Fix configuration.",
        "how_to_verify": "Run verification curl."
    }

    # Mock health to ready, and generate_completion to return json
    with patch.object(ollama_service, "check_health", return_value={"status_code": "ready", "status": "online"}):
        with patch.object(ollama_service, "generate_completion", return_value=json.dumps(mock_ollama_res)):
            res = client.post("/api/ai/explain-finding", json={"finding_id": f["id"]})
            assert res.status_code == 200
            data = res.json()
            assert data["ai_provider"] == "ollama"
            assert data["explanation"]["ai_provider"] == "ollama"


def test_ai_provenance_analyze_finding_endpoint():
    """Verify POST /api/findings/{id}/analyze returns ai_provider: 'ollama' when Ollama succeeds."""
    import json
    findings_res = client.get("/api/findings?is_demo=true")
    f = findings_res.json()[0]

    mock_ollama_res = {
        "what_was_found": "Ollama generated finding summary.",
        "where": "/api/v1/resource",
        "why_it_matters": "Ollama hypothesis.",
        "possible_impact": "High risk impact.",
        "severity_rationale": "Clear rationale.",
        "recommended_action": "Apply patch.",
        "how_to_fix": "Fix configuration.",
        "how_to_verify": "Run verification curl."
    }

    with patch.object(ollama_service, "check_health", return_value={"status_code": "ready", "status": "online"}):
        with patch.object(ollama_service, "generate_completion", return_value=json.dumps(mock_ollama_res)):
            res = client.post(f"/api/findings/{f['id']}/analyze")
            assert res.status_code == 200
            data = res.json()
            assert data["success"] is True
            assert data["ai_provider"] == "ollama"
            assert data["updated_finding"]["ai_provider"] == "ollama"
            assert data["updated_finding"]["ai_analysis_status"] == "COMPLETED"


