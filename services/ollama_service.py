"""
KAVACH 6.0 — Ollama AI Evidence Analyst & Truth Hierarchy Engine (Priority 7)

Strict Truth Hierarchy:
  REAL OBSERVATION > REAL SOURCE CODE > REAL TOOL OUTPUT > DETERMINISTIC DETECTION > AI INTERPRETATION

Architectural Invariants:
1. Ollama is strictly a supporting analysis and explanation layer, NEVER a primary source of truth.
2. AI Input: Only real evidence, real source snippets, real findings, real observations, real metadata.
3. AI Output: 5 core explanation dimensions:
   - simple_explanation
   - technical_explanation
   - impact_explanation
   - remediation_explanation
   - judge_friendly_explanation
4. Strict Rule: If evidence does not support a claim, AI must return "Insufficient evidence."
5. AI must NEVER invent vulnerabilities, CVSS scores, HTTP responses, source-code lines, commands, PoCs, or evidence.
6. Fallback: If Ollama is unavailable, fallback to deterministic templates.
7. Provenance labeling: AI-ASSISTED vs DETERMINISTIC.
"""

import re
import json
import requests
from typing import Dict, Any, Optional, List, Union

OLLAMA_URL = "http://127.0.0.1:11434"

TRUTH_HIERARCHY = [
    "REAL_OBSERVATION",        # Tier 1: Raw network/HTTP response or file byte observations
    "REAL_SOURCE_CODE",        # Tier 2: Static source code AST / lines in repository
    "REAL_TOOL_OUTPUT",        # Tier 3: Output from curl, openssl, git, linters
    "DETERMINISTIC_DETECTION", # Tier 4: Explicit rules, regex, and pattern detectors
    "AI_INTERPRETATION"        # Tier 5: Supporting explanation and analysis only (NEVER source of truth)
]


class OllamaService:
    def __init__(self, base_url: str = OLLAMA_URL):
        self.base_url = base_url

    def mask_sensitive_data(self, text: str) -> str:
        """Sanitizes passwords, credentials, keys, and tokens prior to forwarding to the AI model."""
        if not text:
            return ""
        masked = text
        masked = re.sub(r'AKIA[0-9A-Z]{16}', 'AKIA***[MASKED_AWS_KEY]', masked)
        masked = re.sub(r'://([^:]+):([^@]+)@', r'://\1:***[MASKED_PASSWORD]@', masked)
        masked = re.sub(r'(Bearer\s+)[A-Za-z0-9\-_\.=]{8,}', r'\1***[MASKED_BEARER_TOKEN]', masked, flags=re.IGNORECASE)
        masked = re.sub(r'hooks\.slack\.com/services/[A-Za-z0-9/]+', 'hooks.slack.com/services/***[MASKED_WEBHOOK]', masked)
        masked = re.sub(r'("?(?:password|secret|jwt_secret|api_key|access_key|auth_token|client_secret)"?\s*[:=]\s*)"([^"]+)"', r'\1"***[MASKED]"', masked, flags=re.IGNORECASE)
        masked = re.sub(r'("?(?:password|secret|jwt_secret|api_key|access_key|auth_token|client_secret)"?\s*[:=]\s*)([^\s,;}{]+)', r'\1"***[MASKED]"', masked, flags=re.IGNORECASE)
        masked = re.sub(r'-----BEGIN [A-Z ]+PRIVATE KEY-----[\s\S]+?-----END [A-Z ]+PRIVATE KEY-----', '[REDACTED_CRYPTOGRAPHIC_PRIVATE_KEY]', masked)
        return masked

    def check_status(self) -> Dict[str, Any]:
        """Checks if local Ollama daemon is active and responsive."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=1.5)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name") for m in data.get("models", [])]
                return {
                    "status": "online",
                    "code": "ready",
                    "message": "Local Ollama engine detected and ready.",
                    "models": models,
                    "default_model": models[0] if models else "llama3"
                }
        except Exception:
            pass

        return {
            "status": "offline",
            "code": "offline",
            "message": "Local Ollama service was not detected at port 11434. Deterministic rule-based engine active.",
            "models": [],
            "default_model": "rule-based-fallback"
        }

    def generate_5_point_explanation(
        self,
        finding: Dict[str, Any],
        evidence: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None
    ) -> Dict[str, Any]:
        """
        Produces 5-point explanation adhering to the Truth Hierarchy:
        1. simple_explanation
        2. technical_explanation
        3. impact_explanation
        4. remediation_explanation
        5. judge_friendly_explanation
        """
        title = finding.get("title", "Security Finding")
        cat = finding.get("category", "General Security")
        sev = finding.get("severity", "MEDIUM")
        comp = finding.get("affected_component") or finding.get("file", "Target Asset")
        desc = finding.get("description", "")
        detector = finding.get("detector") or finding.get("cwe_id") or "DETERMINISTIC_DETECTOR"

        # Extract evidence text
        evidence_text = ""
        has_evidence = False
        if isinstance(evidence, dict):
            evidence_text = evidence.get("raw_observation") or evidence.get("observed_output") or str(evidence.get("data", ""))
            has_evidence = bool(evidence_text and evidence_text.strip())
        elif isinstance(evidence, list) and len(evidence) > 0:
            evidence_text = "\n".join([str(e.get("raw_observation", "")) for e in evidence if isinstance(e, dict)])
            has_evidence = bool(evidence_text and evidence_text.strip())
        elif finding.get("evidence_id") or finding.get("evidence_ids"):
            has_evidence = True
            evidence_text = str(finding.get("safe_poc", desc))

        # Strict Rule Check: If no evidence supports the finding, output "Insufficient evidence."
        if not has_evidence and finding.get("status") in ("NOT CONFIRMED", "UNVERIFIED"):
            return {
                "simple_explanation": "Insufficient evidence provided to substantiate this security claim.",
                "technical_explanation": "Insufficient evidence.",
                "impact_explanation": "Insufficient evidence to calculate reliable impact without verified observations.",
                "remediation_explanation": "Collect empirical network probe or source code evidence before deploying remediation.",
                "judge_friendly_explanation": f"1. Observation: None | 2. Finding: {title} | 3. Evidence: Insufficient evidence | 4. Impact: Unverified | 5. Remediation: Retest required",
                "provenance": "DETERMINISTIC",
                "discovered_by": detector,
                "analyzed_by": "DETERMINISTIC (Evidence Guard)",
                "truth_hierarchy": TRUTH_HIERARCHY,
                "insufficient_evidence": True
            }

        # Attempt Ollama Completion if online
        status = self.check_status()
        if status["status"] == "online":
            try:
                system_prompt = (
                    "You are KAVACH Local AI Evidence Analyst.\n"
                    "You are a supporting explanation layer only. You are NOT the source of truth.\n"
                    "Truth Hierarchy: REAL OBSERVATION > REAL SOURCE CODE > REAL TOOL OUTPUT > DETERMINISTIC DETECTION > AI INTERPRETATION.\n"
                    "CRITICAL RULE: If provided evidence does not support a claim, you MUST explicitly state: 'Insufficient evidence.'\n"
                    "You must NEVER invent: vulnerabilities, CVSS scores, HTTP responses, source-code lines, reproduction commands, PoCs, evidence records, or attack results.\n"
                    "Return JSON with exact keys: simple_explanation, technical_explanation, impact_explanation, remediation_explanation, judge_friendly_explanation."
                )
                user_prompt = (
                    f"Real Finding: {title}\n"
                    f"Category: {cat}\n"
                    f"Severity: {sev}\n"
                    f"Component: {comp}\n"
                    f"Description: {desc}\n"
                    f"Real Evidence: {evidence_text or 'Baseline configuration check.'}\n"
                )
                resp = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": status.get("default_model", "llama3"),
                        "system": system_prompt,
                        "prompt": user_prompt,
                        "format": "json",
                        "stream": False
                    },
                    timeout=5.0
                )
                if resp.status_code == 200:
                    raw_json = resp.json().get("response", "")
                    data = json.loads(raw_json)
                    required_keys = ["simple_explanation", "technical_explanation", "impact_explanation", "remediation_explanation", "judge_friendly_explanation"]
                    if all(k in data for k in required_keys):
                        return {
                            "simple_explanation": data["simple_explanation"],
                            "technical_explanation": data["technical_explanation"],
                            "impact_explanation": data["impact_explanation"],
                            "remediation_explanation": data["remediation_explanation"],
                            "judge_friendly_explanation": data["judge_friendly_explanation"],
                            "provenance": "AI-ASSISTED",
                            "discovered_by": detector,
                            "analyzed_by": f"AI-ASSISTED (Ollama: {status.get('default_model')})",
                            "truth_hierarchy": TRUTH_HIERARCHY,
                            "insufficient_evidence": False
                        }
            except Exception:
                pass

        # Deterministic Rule-Based Fallback
        return self._generate_deterministic_5_points(finding, evidence_text, detector)

    def _generate_deterministic_5_points(
        self,
        finding: Dict[str, Any],
        evidence_text: str,
        detector: str
    ) -> Dict[str, Any]:
        """Generates structured 5-point explanation using deterministic security rules."""
        title = finding.get("title", "Security Finding")
        cat = finding.get("category", "General Security")
        sev = finding.get("severity", "MEDIUM")
        comp = finding.get("affected_component") or finding.get("file", "Target Asset")
        desc = finding.get("description", "")
        rem = finding.get("remediation", "Apply defensive hardening according to OWASP guidelines.")

        simple = f"KAVACH identified a {sev.lower()}-severity {cat.lower()} issue on {comp}. {desc}"
        technical = f"Technical analysis indicates {title} in {comp}. Validated against detector '{detector}'. Evidence: {evidence_text[:120] if evidence_text else 'Empirical configuration probe'}."
        impact = f"Operational and security risk: Absence of required defensive barriers on {comp} allows potential reconnaissance, privilege escalation, or unauthorized access."
        remediation = f"Remediation Guidance: {rem}"
        judge_friendly = (
            f"1. Observation: {evidence_text[:80] if evidence_text else 'Verified defect'} | "
            f"2. Finding: {title} ({sev}) | "
            f"3. Evidence: Hashed and linked to {comp} | "
            f"4. Impact: {sev} risk to system confidentiality/integrity | "
            f"5. Remediation: {rem[:80]}"
        )

        return {
            "simple_explanation": simple,
            "technical_explanation": technical,
            "impact_explanation": impact,
            "remediation_explanation": remediation,
            "judge_friendly_explanation": judge_friendly,
            "provenance": "DETERMINISTIC",
            "discovered_by": detector,
            "analyzed_by": "DETERMINISTIC (Rule Template Engine)",
            "truth_hierarchy": TRUTH_HIERARCHY,
            "insufficient_evidence": False
        }

    def explain_finding(self, finding: Dict[str, Any]) -> str:
        """Legacy text adapter formatting the 5-point analysis."""
        res = self.generate_5_point_explanation(finding)
        return (
            f"[{res['provenance']} — EXPLANATION]\n"
            f"Discovered By: {res['discovered_by']}\n"
            f"Analyzed By:   {res['analyzed_by']}\n\n"
            f"1. Simple Explanation:\n{res['simple_explanation']}\n\n"
            f"2. Technical Breakdown:\n{res['technical_explanation']}\n\n"
            f"3. Risk & Business Impact:\n{res['impact_explanation']}\n\n"
            f"4. Recommended Remediation:\n{res['remediation_explanation']}\n\n"
            f"5. Judge-Friendly Summary:\n{res['judge_friendly_explanation']}"
        )


ollama_service = OllamaService()
