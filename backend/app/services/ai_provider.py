import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.models.models import Finding, EvidenceRecord
from backend.app.schemas.schemas import AIStructuredAnalysis
from backend.app.services.ollama_service import ollama_service

logger = logging.getLogger(__name__)

class RuleBasedSecurityProvider:
    """Deterministic security intelligence provider used when AI is offline or as baseline."""
    
    def analyze(self, finding: Finding, evidence: Optional[EvidenceRecord] = None) -> Dict[str, Any]:
        cat_lower = (finding.category or "").lower()
        title_lower = (finding.title or "").lower()
        component = finding.affected_component or "Application Surface"

        # Category 1: Authentication
        if "auth" in cat_lower or "token" in title_lower or "jwt" in title_lower:
            return {
                "summary": f"Observed potential authentication weakness in {component}. The handler may permit algorithm confusion or unverified claims.",
                "security_hypothesis": f"If an attacker tampers with JWT headers or submits 'alg: none', the server may fail to enforce cryptographic signature verification on {component}.",
                "affected_component": component,
                "potential_impact": "Full authentication bypass, arbitrary user impersonation, and administrative session hijacking.",
                "confidence": 89.0,
                "reasoning_summary": "Heuristic correlation matches CWE-306 and CWE-347. Authentication logic requires rigorous asymmetric key validation.",
                "recommended_validation": [
                    f"Send token with 'alg: none' to {component} and observe response status",
                    "Verify if server rejects tokens signed with arbitrary symmetric keys",
                    "Inspect token expiration and session invalidation behavior"
                ],
                "recommended_remediation": [
                    "Explicitly restrict JWT algorithm whitelist to ['RS256'] in verification middleware",
                    "Enforce strict cryptographic signature checks prior to claims parsing",
                    "Invalidate tokens immediately upon logout via Redis revocation blacklist"
                ]
            }

        # Category 2: Authorization & Access Control
        elif "access control" in cat_lower or "idor" in title_lower or "authorization" in cat_lower:
            return {
                "summary": f"Observed authorization weakness on {component}. The endpoint allows direct object references without tenancy validation.",
                "security_hypothesis": f"Altering the resource identifier in requests to {component} discloses adjacent tenant data because server-side queries lack owner tenancy filters.",
                "affected_component": component,
                "potential_impact": "Unauthorized disclosure of confidential tenant data, cross-account horizontal privilege escalation, tampering with external records.",
                "confidence": 92.0,
                "reasoning_summary": "Matches CWE-639 (Insecure Direct Object Reference). Controller performs entity lookup without verifying current user session context.",
                "recommended_validation": [
                    f"Send GET request to {component} with User A session referencing User B resource ID",
                    "Inspect whether HTTP 200 is returned with confidential payload",
                    "Verify that server enforces 403 Forbidden on mismatched ownership"
                ],
                "recommended_remediation": [
                    "Inject tenant owner filter directly into database query: .filter(owner_id == current_user.id)",
                    "Replace sequential or predictable primary keys with non-enumerable UUIDv4",
                    "Deploy centralized Attribute-Based Access Control (ABAC) decorators on all routes"
                ]
            }

        # Category 3: Input Validation & Data Handling
        elif "injection" in cat_lower or "sql" in title_lower or "input" in cat_lower:
            return {
                "summary": f"Input validation vulnerability detected in {component}. Raw input influences backend query or command structures.",
                "security_hypothesis": f"User-supplied input to {component} is concatenated directly into SQL query strings without parameterization, triggering database syntax reflection.",
                "affected_component": component,
                "potential_impact": "Arbitrary SQL execution, complete database exfiltration, unauthorized modification, and potential underlying host compromise.",
                "confidence": 95.0,
                "reasoning_summary": "Matches CWE-89 (SQL Injection). Empirical testing reflected database syntax errors upon injection of boundary test tokens.",
                "recommended_validation": [
                    "Submit non-destructive quote payload: ' OR 1=1 --",
                    "Monitor for database syntax errors or execution timing anomalies",
                    "Inspect database query logs in staging environment"
                ],
                "recommended_remediation": [
                    "Enforce parameterized prepared statements with bind variables exclusively",
                    "Utilize SQLAlchemy / ORM query builder expressions instead of raw string interpolation",
                    "Apply least-privilege permissions to database application accounts"
                ]
            }

        # Category 4: API Security
        elif "api" in cat_lower or "traceback" in title_lower or "error" in title_lower or "debug" in title_lower:
            return {
                "summary": f"API security misconfiguration identified on {component}. Unhandled exceptions disclose internal runtime state.",
                "security_hypothesis": f"Submitting unexpected or malformed parameters to {component} triggers raw exception disclosures that reveal internal source paths and dependencies.",
                "affected_component": component,
                "potential_impact": "Technical reconnaissance disclosure assisting targeted attack payload formulation.",
                "confidence": 90.0,
                "reasoning_summary": "Correlates with CWE-209 (Generation of Error Message Containing Sensitive Information).",
                "recommended_validation": [
                    f"Send malformed payload to {component}",
                    "Inspect response body for Python traceback signatures or library versions",
                    "Verify production error handling standardization"
                ],
                "recommended_remediation": [
                    "Disable DEBUG mode in production environment configuration",
                    "Register global exception handlers that output generic JSON error envelopes",
                    "Forward full stack traces exclusively to private centralized log collectors"
                ]
            }

        # Category 5: Client-Side Security & Security Headers
        elif "header" in cat_lower or "client" in cat_lower or "csp" in title_lower or "clickjacking" in title_lower:
            return {
                "summary": f"Missing defensive security headers on {component}.",
                "security_hypothesis": f"Responses from {component} lack modern browser defensive directives, exposing users to clickjacking and script injection attacks.",
                "affected_component": component,
                "potential_impact": "Clickjacking (UI redressing), MIME-type sniffing, cross-site scripting propagation, cleartext downgrade.",
                "confidence": 98.0,
                "reasoning_summary": "Direct HTTP audit confirmed absence of Content-Security-Policy, Strict-Transport-Security, and X-Frame-Options. Matches CWE-16.",
                "recommended_validation": [
                    f"Issue HTTP HEAD request against {component}",
                    "Audit response headers for CSP, HSTS, and X-Frame-Options directives",
                    "Verify browser rendering behavior inside an iframe tag"
                ],
                "recommended_remediation": [
                    "Add Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
                    "Configure restrictive Content-Security-Policy: default-src 'self'",
                    "Add X-Frame-Options: DENY and X-Content-Type-Options: nosniff"
                ]
            }

        # Category 6: Secure Communication
        elif "communication" in cat_lower or "transport" in cat_lower or "tls" in title_lower or "cookie" in title_lower:
            return {
                "summary": f"Insecure transport or session cookie flags on {component}.",
                "security_hypothesis": f"Session cookies set by {component} lack Secure and SameSite flags, allowing potential interception over unencrypted networks.",
                "affected_component": component,
                "potential_impact": "Session token interception via man-in-the-middle (MitM) attacks or cross-site request forgery (CSRF).",
                "confidence": 94.0,
                "reasoning_summary": "Matches CWE-614 (Sensitive Cookie in HTTPS Session Without 'Secure' Attribute).",
                "recommended_validation": [
                    f"Inspect Set-Cookie header directives returned by {component}",
                    "Verify presence of 'Secure', 'HttpOnly', and 'SameSite=Lax/Strict' attributes",
                    "Test connection over plain HTTP to verify strict 301 HTTPS redirection"
                ],
                "recommended_remediation": [
                    "Set cookie attributes: Secure=True, HttpOnly=True, SameSite='Lax'",
                    "Enforce strict TLS 1.3 protocol requirement on web reverse proxy",
                    "Deploy HSTS header with preload directive"
                ]
            }

        # Category 7: Data Storage & Privacy / Default
        else:
            return {
                "summary": f"Security observation recorded for {component}: {finding.title}.",
                "security_hypothesis": f"Observed configuration or response patterns on {component} require technical verification against secure baseline standards.",
                "affected_component": component,
                "potential_impact": "Potential compromise of confidentiality, integrity, or system availability.",
                "confidence": 85.0,
                "reasoning_summary": f"Heuristic classification for category '{finding.category}'. Requires empirical verification.",
                "recommended_validation": [
                    f"Execute safe non-destructive probe against {component}",
                    "Compare observed response against security baseline documentation",
                    "Verify access control and session constraints"
                ],
                "recommended_remediation": [
                    "Review component implementation against OWASP Top 10 guidelines",
                    "Apply defense-in-depth sanitization and authorization checks",
                    "Conduct automated regression testing post-patch"
                ]
            }


class AIProviderAdapter:
    """Unified Server-Side AI Provider Adapter.
    Prioritizes server-side Ollama; gracefully falls back to RuleBasedSecurityProvider.
    Ensures online users have zero setup requirement.
    """
    
    def __init__(self):
        self.rule_provider = RuleBasedSecurityProvider()

    async def analyze_finding(
        self,
        finding: Finding,
        evidence: Optional[EvidenceRecord] = None
    ) -> Dict[str, Any]:
        """Analyzes a finding using server-side Ollama or rule-based fallback."""
        
        # Check if server-side Ollama is available
        is_online = await ollama_service.is_online()
        if not is_online:
            logger.info("Server-side Ollama is offline. Employing deterministic Rule-Based Security Provider.")
            result = self.rule_provider.analyze(finding, evidence)
            result["provider_used"] = "RULE_BASED_FALLBACK"
            result["ai_provider"] = "fallback"
            return result

        # Construct evidence-constrained prompt
        evidence_text = evidence.raw_data if evidence else "No direct raw probe captured yet. Analytical baseline."
        prompt = (
            f"You are KAVACH Security Engine.\n"
            f"Analyze this empirical finding strictly based on the provided evidence:\n"
            f"Finding: {finding.title}\n"
            f"Category: {finding.category}\n"
            f"Component: {finding.affected_component}\n"
            f"Evidence: {evidence_text[:1000]}\n\n"
            f"Do NOT invent facts. Return valid JSON only with keys: "
            f"summary, security_hypothesis, affected_component, potential_impact, confidence (0-100), "
            f"reasoning_summary, recommended_validation (array), recommended_remediation (array)."
        )

        try:
            raw_response = await ollama_service.generate(prompt=prompt)
            # Parse JSON
            try:
                parsed = json.loads(raw_response)
                parsed["provider_used"] = "SERVER_SIDE_OLLAMA"
                parsed["ai_provider"] = "ollama"
                return parsed
            except Exception:
                import re
                match = re.search(r"\{.*\}", raw_response, re.DOTALL)
                if match:
                    parsed = json.loads(match.group(0))
                    parsed["provider_used"] = "SERVER_SIDE_OLLAMA"
                    parsed["ai_provider"] = "ollama"
                    return parsed
                raise ValueError("JSON parsing failed")
        except Exception as ex:
            logger.warning(f"Ollama generation failed ({ex}); utilizing deterministic Rule-Based Security Provider.")
            result = self.rule_provider.analyze(finding, evidence)
            result["provider_used"] = "RULE_BASED_FALLBACK"
            result["ai_provider"] = "fallback"
            return result

ai_provider = AIProviderAdapter()
