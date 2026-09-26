"""
Regression tests for KAVACH 5.0 — Finding-Specific Evidence Grounding (WM-API-DOCS-A018).
Ensures:
1. Authoritative local knowledge chunk for CWE-200 API documentation exposure exists and is indexed.
2. Retrieval for WM-API-DOCS-A018 prioritizes CWE-200 API documentation and schema exposure.
3. Unrelated clickjacking and defensive HTTP security header chunks (DOC-CWE-16-HEADERS) are NOT selected as primary sources.
4. AI explanation is strictly grounded in evidence:
   - WHAT WAS FOUND: Unauthenticated /openapi.json returned HTTP 200
   - WHY IT MATTERS: Public schema aids reconnaissance; not proof of unauthorized API access
   - POSSIBLE IMPACT: Information exposure aiding reconnaissance (no hallucinated data extraction, privilege escalation, clickjacking)
   - RECOMMENDED ACTION / HOW TO FIX: Production documentation restriction, schema filtering
   - HOW TO VERIFY: Probe unauthenticated access to /openapi.json
5. "AI Confidence != Vulnerability Confirmation." principle is strictly preserved.
"""

import pytest
import asyncio
from backend.app.core.database import SessionLocal
from backend.app.models.models import Finding, EvidenceRecord
from backend.app.rag.document_loader import STATIC_SECURITY_KNOWLEDGE
from backend.app.rag.retriever import rag_retriever
from backend.app.services.ai_analysis_service import ai_analysis_service
from backend.app.services.validation_service import validation_service


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_cwe200_authoritative_document_exists():
    """Verify that DOC-CWE-200-APIDOCS exists in STATIC_SECURITY_KNOWLEDGE with all required criteria."""
    doc = next((d for d in STATIC_SECURITY_KNOWLEDGE if d.id == "DOC-CWE-200-APIDOCS"), None)
    assert doc is not None, "DOC-CWE-200-APIDOCS must exist in STATIC_SECURITY_KNOWLEDGE"
    assert doc.cwe_id == "CWE-200"
    assert "OWASP-A05" in (doc.owasp_category or "")
    assert doc.category == "API Security"

    content_lower = doc.content.lower()
    # 1. Explains what information exposure means
    assert "information" in content_lower and "exposure" in content_lower
    # 2. How public API schemas can aid reconnaissance
    assert "reconnaissance" in content_lower and "openapi" in content_lower
    # 3. That exposure of documentation is not automatically proof of unauthorized API access
    assert "not automatically proof" in content_lower
    # 4. That impact depends on what sensitive info/endpoints are disclosed
    assert "depends" in content_lower and "sensitive" in content_lower

    # Remediation steps verification
    remediation_text = " ".join(doc.remediation_steps).lower()
    assert "restrict" in remediation_text or "disable" in remediation_text
    assert "production" in remediation_text
    assert "admin" in remediation_text or "deprecated" in remediation_text


def test_wm_api_docs_retrieval_prioritizes_cwe200(db_session):
    """
    Verify that finding-aware retrieval for WM-API-DOCS-A018 prioritizes CWE-200
    and does NOT select clickjacking/header-hardening as the primary source.
    """
    async def _run():
        finding = db_session.query(Finding).filter(Finding.id == "WM-API-DOCS-A018").first()
        assert finding is not None, "Finding WM-API-DOCS-A018 must exist in database"

        evidence = db_session.query(EvidenceRecord).filter(EvidenceRecord.id == "EV-WM-API-DOCS-A018").first()
        assert evidence is not None, "Evidence EV-WM-API-DOCS-A018 must exist in database"

        retrieved, mode, model = await rag_retriever.retrieve_for_finding(finding, evidence, top_k=4)

        assert len(retrieved) > 0, "Retrieval should return security knowledge chunks"

        # Top chunk MUST be CWE-200 / API documentation exposure
        top_chunk = retrieved[0]
        assert top_chunk.cwe_id == "CWE-200", f"Expected top chunk to be CWE-200, got {top_chunk.cwe_id} ({top_chunk.title})"
        assert top_chunk.document_id in ("DOC-CWE-200-APIDOCS", "DOC-DB-CWE-200")

        # Verify unrelated clickjacking / headers chunks are excluded from top grounding sources
        retrieved_doc_ids = [r.document_id for r in retrieved]
        assert "DOC-CWE-16-HEADERS" not in retrieved_doc_ids, "DOC-CWE-16-HEADERS must NOT be selected as primary grounding for API docs"

        for r in retrieved:
            title_lower = r.title.lower()
            assert "clickjacking" not in title_lower, f"Clickjacking chunk unexpectedly present in retrieval: {r.title}"
    asyncio.run(_run())


def test_raw_query_for_api_docs_excludes_unrelated_headers():
    """Verify that general retrieval with API docs query excludes DOC-CWE-16-HEADERS."""
    async def _run():
        query = "Publicly Exposed Interactive API Schema & Documentation API Security CWE-200 OWASP-A05:2021 - Security Misconfiguration"
        retrieved, mode, model = await rag_retriever.retrieve(query, top_k=4)

        assert len(retrieved) > 0
        top_chunk = retrieved[0]
        assert top_chunk.cwe_id == "CWE-200"
        assert top_chunk.document_id == "DOC-CWE-200-APIDOCS"

        retrieved_doc_ids = [r.document_id for r in retrieved]
        assert "DOC-CWE-16-HEADERS" not in retrieved_doc_ids
    asyncio.run(_run())


def test_ai_analysis_7_sections_evidence_grounded(db_session):
    """
    Verify that AI explanation for WM-API-DOCS-A018 produces the exact 7 deterministic,
    evidence-grounded sections without fabricating unproven impacts.
    """
    async def _run():
        finding = db_session.query(Finding).filter(Finding.id == "WM-API-DOCS-A018").first()
        evidence = db_session.query(EvidenceRecord).filter(EvidenceRecord.id == "EV-WM-API-DOCS-A018").first()

        explanation = await ai_analysis_service.explain_finding(finding, evidence)

        # 1. Verify 7 keys exist
        required_keys = [
            "what_was_found",
            "where",
            "why_it_matters",
            "possible_impact",
            "recommended_action",
            "how_to_fix",
            "how_to_verify"
        ]
        for key in required_keys:
            assert key in explanation, f"Missing required key: {key}"
            assert explanation[key], f"Key {key} must not be empty"

        # 2. Verify OBSERVED FACT in what_was_found
        what = explanation["what_was_found"]
        assert "/openapi.json" in what
        assert "200" in what

        # 3. Verify SUPPORTED INTERPRETATION in why_it_matters
        why = explanation["why_it_matters"].lower()
        assert "reconnaissance" in why
        assert "not automatically proof" in why or "not proof" in why

        # 4. Verify NOT PROVEN statements in possible_impact
        impact = explanation["possible_impact"].lower()
        assert "reconnaissance" in impact
        assert "not prove" in impact or "not proven" in impact
        assert "data extraction" in impact
        assert "privilege escalation" in impact
        assert "account compromise" in impact
        assert "lateral movement" in impact
        assert "clickjacking" in impact

        # Ensure unproven impacts are NOT stated as demonstrated impacts
        assert "clickjacking attack demonstrated" not in impact
        assert "database compromised" not in impact
        assert "credentials exfiltrated" not in impact

        # 5. Verify REMEDIATION is focused on API docs, not generic protection headers
        remediation = (explanation["recommended_action"] + " " + explanation["how_to_fix"]).lower()
        assert "restrict" in remediation or "disable" in remediation
        assert "production" in remediation
        assert "protection headers" not in remediation

        # 6. Verify HOW TO VERIFY checks /openapi.json
        verify = explanation["how_to_verify"]
        assert "/openapi.json" in verify
        assert "401" in verify or "403" in verify or "404" in verify

        # 7. Verify core principle is preserved
        assert explanation.get("core_principle") == "AI Confidence != Vulnerability Confirmation."
    asyncio.run(_run())


def test_terminal_verification_targets_openapi(db_session):
    """Verify that validation_service.get_terminal_verification targets /openapi.json for WM-API-DOCS-A018."""
    term_resp = validation_service.get_terminal_verification(db_session, "WM-API-DOCS-A018")
    assert term_resp is not None
    assert "/openapi.json" in term_resp["command"]
    assert term_resp["cwe_id"] == "CWE-200"
    assert "A05" in (term_resp["owasp_category"] or "")
    assert "401" in term_resp["expected_output"] or "403" in term_resp["expected_output"] or "404" in term_resp["expected_output"]
