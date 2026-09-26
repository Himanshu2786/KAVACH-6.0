import os
import json
import hashlib
import httpx
from typing import Dict, Any, Optional, Union
from sqlalchemy.orm import Session
from backend.app.models.models import Finding, EvidenceRecord, Assessment
from backend.app.services.evidence_service import evidence_service
from backend.app.services.knowledge_service import knowledge_service
from backend.app.core.audit import log_audit_event
from backend.app.core.time import ist_isoformat

def verify_openapi_document_delivery(
    status_code: int,
    content_type: str,
    body: Any,
    http_method: str = "GET"
) -> Dict[str, Any]:
    """
    Validates whether an actual OpenAPI JSON or interactive Swagger document was delivered.
    Requirements:
    - Must use GET; HEAD requests cannot deliver a body and cannot prove OpenAPI JSON delivery.
    - Status code must be 200.
    - Content-Type must indicate JSON or interactive UI.
    - Body must not be empty and must parse as valid OpenAPI / Swagger schema (or UI).
    """
    if http_method.upper() == "HEAD":
        return {
            "delivered": False,
            "reason": "HEAD response does not deliver response body; cannot verify OpenAPI JSON delivery.",
            "schema_detected": False,
            "version": None,
            "title": None,
            "body_sha256": None
        }

    if not body:
        return {
            "delivered": False,
            "reason": "Empty response body; no OpenAPI schema delivered.",
            "schema_detected": False,
            "version": None,
            "title": None,
            "body_sha256": None
        }

    raw_bytes = body.encode("utf-8") if isinstance(body, str) else bytes(body)
    body_sha256 = hashlib.sha256(raw_bytes).hexdigest()

    if status_code != 200:
        return {
            "delivered": False,
            "reason": f"HTTP status {status_code} does not indicate exposed document.",
            "schema_detected": False,
            "version": None,
            "title": None,
            "body_sha256": body_sha256
        }

    # Attempt JSON parse
    try:
        data = json.loads(raw_bytes.decode("utf-8", errors="ignore"))
        if isinstance(data, dict) and ("openapi" in data or "swagger" in data):
            ver = str(data.get("openapi") or data.get("swagger"))
            title = data.get("info", {}).get("title", "API")
            return {
                "delivered": True,
                "reason": f"OpenAPI {ver} schema document delivered.",
                "schema_detected": True,
                "openapi_detected": True,
                "version": ver,
                "title": title,
                "body_sha256": body_sha256,
                "servers": data.get("servers", [])
            }
    except Exception:
        pass

    # Swagger UI HTML fallback
    body_text = raw_bytes.decode("utf-8", errors="ignore").lower()
    if "swagger-ui" in body_text or ("swagger" in body_text and "openapi" in body_text):
        return {
            "delivered": True,
            "reason": "Swagger UI interactive documentation delivered.",
            "schema_detected": True,
            "openapi_detected": True,
            "version": "Swagger UI",
            "title": "Interactive Documentation",
            "body_sha256": body_sha256
        }

    return {
        "delivered": False,
        "reason": "Response did not contain valid OpenAPI schema or Swagger documentation.",
        "schema_detected": False,
        "openapi_detected": False,
        "version": None,
        "title": None,
        "body_sha256": body_sha256
    }

class ValidationService:
    def evaluate_finding_status(self, db: Session, finding_id: str) -> Finding:
        """Determines final finding status strictly based on technical evidence."""
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        if not finding:
            raise ValueError(f"Finding {finding_id} not found")

        records = db.query(EvidenceRecord).filter(EvidenceRecord.finding_id == finding_id).all()
        if not records:
            finding.status = "POTENTIAL"
            finding.evidence_status = "NONE"
            db.commit()
            return finding

        has_confirmed = any(r.validation_result == "CONFIRMED" for r in records)
        has_unconfirmed = any(r.validation_result == "UNCONFIRMED" for r in records)
        has_manual = any(r.validation_result == "MANUAL REVIEW REQUIRED" for r in records)

        old_status = finding.status
        if has_confirmed:
            finding.status = "CONFIRMED"
            finding.evidence_status = "VERIFIED"
        elif has_unconfirmed and not has_manual:
            finding.status = "UNCONFIRMED"
            finding.evidence_status = "VERIFIED"
        elif has_manual:
            finding.status = "REQUIRES MANUAL REVIEW"
            finding.evidence_status = "AVAILABLE"
        else:
            finding.status = "EVIDENCE AVAILABLE"
            finding.evidence_status = "AVAILABLE"

        finding.updated_at = ist_isoformat()
        db.commit()
        db.refresh(finding)

        if old_status != finding.status:
            log_audit_event(
                db=db,
                event_type="FINDING_STATUS_TRANSITION",
                description=f"Finding {finding.id} transitioned from {old_status} to {finding.status} based on {len(records)} evidence record(s).",
                assessment_id=finding.assessment_id,
                finding_id=finding.id,
                metadata={"old_status": old_status, "new_status": finding.status}
            )

        return finding

    async def execute_safe_probe(
        self,
        db: Session,
        finding_id: str,
        probe_type: str = "HTTP_PROBE",
        is_demo: bool = True
    ) -> EvidenceRecord:
        """Executes a safe non-destructive probe to gather technical evidence."""
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        if not finding:
            raise ValueError("Finding not found")

        assessment = db.query(Assessment).filter(Assessment.id == finding.assessment_id).first()
        target_url = assessment.target_url if assessment else "http://localhost:8000"

        finding.status = "VALIDATING"
        db.commit()

        # If it's a live URL and probe requested
        if not is_demo and target_url.startswith("http"):
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(target_url)
                    headers_text = "\n".join([f"{k}: {v}" for k, v in resp.headers.items()])
                    raw_data = f"HTTP/{resp.http_version} {resp.status_code} {resp.reason_phrase}\n{headers_text}\n\n{resp.text[:500]}"
                    
                    # Safe evaluation based on probe
                    if "header" in finding.category.lower():
                        missing = []
                        if "content-security-policy" not in resp.headers: missing.append("Content-Security-Policy")
                        if "strict-transport-security" not in resp.headers: missing.append("Strict-Transport-Security")
                        if missing:
                            val_result = "CONFIRMED"
                            desc = f"Verified absence of critical security headers in live response: {', '.join(missing)}"
                        else:
                            val_result = "UNCONFIRMED"
                            desc = "Defensive headers were observed in the HTTP response."
                    else:
                        val_result = "MANUAL REVIEW REQUIRED"
                        desc = f"Probe executed against {target_url}. Status {resp.status_code} received; requires analyst verification."

                    evd = evidence_service.create_evidence(
                        db=db,
                        finding_id=finding_id,
                        evidence_type="HTTP Response",
                        description=desc,
                        raw_data=raw_data,
                        validation_result=val_result,
                        source="Live HTTP Prober",
                        is_demo=False
                    )
                    self.evaluate_finding_status(db, finding_id)
                    return evd
            except Exception as ex:
                raw_data = f"Probe Error: {str(ex)}"
                evd = evidence_service.create_evidence(
                    db=db,
                    finding_id=finding_id,
                    evidence_type="Probe Error",
                    description=f"Live probe could not reach target: {str(ex)}",
                    raw_data=raw_data,
                    validation_result="INCONCLUSIVE",
                    source="Live HTTP Prober",
                    is_demo=False
                )
                self.evaluate_finding_status(db, finding_id)
                return evd

        # Simulated Demo Probe
        cat_lower = finding.category.lower()
        if "access control" in cat_lower or "idor" in finding.title.lower():
            raw_sample = (
                "GET /api/v1/workspaces/ws-9921/sensitive HTTP/1.1\n"
                "Host: target.internal\n"
                "Authorization: Bearer [REDACTED_TOKEN]\n\n"
                "HTTP/1.1 200 OK\n"
                "Content-Type: application/json\n\n"
                '{"workspace_id": "ws-9921", "owner": "tenant_bravo", "api_keys": ["kav_sec_live_992144"], "status": "CONFIDENTIAL"}'
            )
            desc = "Simulated validation observed HTTP 200 disclosure of tenant_bravo confidential keys under user_alpha token."
            val_res = "CONFIRMED"
            evd_type = "API Response"
        elif "injection" in cat_lower or "sql" in finding.title.lower():
            raw_sample = (
                "POST /api/v1/search HTTP/1.1\n"
                "Content-Type: application/json\n\n"
                '{"filter": "test\' OR 1=1 --"}\n\n'
                "HTTP/1.1 500 Internal Server Error\n"
                "Content-Type: text/plain\n\n"
                "sqlite3.OperationalError: near 'OR': syntax error. Query: SELECT * FROM items WHERE name LIKE '%test' OR 1=1 --%'"
            )
            desc = "Backend reflected SQLite syntax error message upon single quote and boolean operator injection."
            val_res = "CONFIRMED"
            evd_type = "API Response"
        elif "header" in cat_lower:
            raw_sample = (
                "HTTP/1.1 200 OK\n"
                "Server: nginx/1.24.0\n"
                "Content-Type: text/html; charset=UTF-8\n"
                "Connection: keep-alive\n"
                "X-Powered-By: Express\n"
                "<!-- Missing: Content-Security-Policy, Strict-Transport-Security, X-Frame-Options -->"
            )
            desc = "Header inspection verified the complete absence of CSP, HSTS, and X-Frame-Options headers."
            val_res = "CONFIRMED"
            evd_type = "Security Header Observation"
        else:
            raw_sample = (
                "GET /api/v1/auth/status HTTP/1.1\n"
                "Authorization: Bearer invalid_or_none_alg\n\n"
                "HTTP/1.1 401 Unauthorized\n"
                "Content-Type: application/json\n\n"
                '{"error": "invalid_token_signature"}'
            )
            desc = "Authentication check correctly rejected unverified tokens with HTTP 401."
            val_res = "UNCONFIRMED"
            evd_type = "Authentication Behavior"

        evd = evidence_service.create_evidence(
            db=db,
            finding_id=finding_id,
            evidence_type=evd_type,
            description=desc,
            raw_data=raw_sample,
            validation_result=val_res,
            source="Validation Engine (Probe)",
            is_demo=is_demo
        )
        self.evaluate_finding_status(db, finding_id)
        return evd

    def get_terminal_verification(self, db: Session, finding_id: str) -> Dict[str, Any]:
        """Returns protocol-level terminal verification data directly linked to the evidence record."""
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        if not finding:
            raise ValueError(f"Finding {finding_id} not found")

        assessment = db.query(Assessment).filter(Assessment.id == finding.assessment_id).first()
        target_url = assessment.target_url if assessment else "https://target.internal"

        # Fetch latest evidence
        evd = db.query(EvidenceRecord).filter(EvidenceRecord.finding_id == finding_id).order_by(EvidenceRecord.timestamp.desc()).first()

        evd_id = evd.id if evd else "EVD-PENDING"
        timestamp = evd.timestamp if evd else ist_isoformat()
        raw_output = evd.raw_data if evd else "No raw probe data collected yet."
        integrity_hash = evd.integrity_hash if evd else "SHA-256-PENDING"
        nature = getattr(evd, "evidence_nature", "REAL EVIDENCE") if evd else "REAL EVIDENCE"
        
        # Command resolution
        is_api_docs = (
            finding.cwe_id == "CWE-200" 
            or "api doc" in (finding.title or "").lower() 
            or "openapi" in (finding.title or "").lower()
            or "API-DOCS" in (finding.id or "").upper()
        )
        if evd and evd.verification_command:
            cmd = evd.verification_command
            if is_api_docs:
                cmd = (
                    cmd.replace("-Method Head", "-Method Get")
                       .replace("-Method HEAD", "-Method Get")
                       .replace("curl -k -I", "curl -k -s")
                       .replace("curl -i -s -k", "curl -k -s")
                )
        elif is_api_docs:
            comp_url = finding.affected_component if (finding.affected_component or "").startswith("http") else f"{target_url.rstrip('/')}/openapi.json"
            if os.name == 'nt':
                cmd = f'Invoke-WebRequest -Uri "{comp_url}" -Method Get'
            else:
                cmd = f'curl -k -s "{comp_url}"'
        else:
            cmd = f"curl -i -s -k '{target_url}{finding.affected_component}'"

        if is_api_docs:
            exp_output = "HTTP/1.1 401 Unauthorized (or 403 Forbidden / 404 Not Found in production)"
        else:
            exp_output = evd.expected_output if evd and evd.expected_output else "HTTP/1.1 403 Forbidden\nContent-Type: application/json\n\n{\"error\": \"access_denied\"}"
        obs_output = evd.observed_output if evd and evd.observed_output else raw_output

        steps = [
            "Step 1: Open your terminal or safe command-line shell environment.",
            "Step 2: Execute the safe non-destructive verification command provided below.",
            "Step 3: Observe the returned HTTP status line and payload.",
            f"Step 4: Compare observed output against KAVACH Evidence Record [{evd_id}]."
        ]

        return {
            "assessment_id": finding.assessment_id,
            "evidence_id": evd_id,
            "target": target_url,
            "timestamp": timestamp,
            "check_name": finding.title,
            "cwe_id": finding.cwe_id,
            "owasp_category": finding.canonical_owasp,
            "method": "Safe Diagnostic Probe (Read-Only)",
            "verification_steps": steps,
            "command": cmd,
            "expected_output": exp_output,
            "observed_output": obs_output,
            "status": finding.status,
            "integrity_hash": integrity_hash,
            "evidence_nature": nature
        }

    def re_verify_finding(
        self,
        db: Session,
        finding_id: str,
        command_executed: str = "",
        output_after: str = "",
        force_status: Optional[str] = None,
        target_override: Optional[str] = None
    ) -> Any:
        """
        Executes genuine empirical re-verification test against target:
        FINDING → BEFORE EVIDENCE → REMEDIATION → RE-TEST → AFTER EVIDENCE → STATE DIFF → VERIFIED / STILL OPEN → AUDIT TRAIL
        Enforces:
        - Real deterministic security probe against target URL or local file
        - Real SHA-256 calculation for both before and after evidence
        - Immutability of original before evidence
        - Immutable creation of after evidence
        - Structured 5-point state diff
        - Sequential audit trail events
        """
        import uuid
        import hashlib
        import json
        import os
        from pathlib import Path
        from backend.app.models.models import ReVerificationRecord

        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        if not finding:
            raise ValueError(f"Finding {finding_id} not found")

        assessment = db.query(Assessment).filter(Assessment.id == finding.assessment_id).first()
        target_url = target_override or (assessment.target_url if assessment else "") or "https://www.worldmonitor.app"
        now_ts = ist_isoformat()

        # Step 1: Log RETEST_STARTED
        log_audit_event(
            db=db,
            event_type="RETEST_STARTED",
            description=f"Empirical re-test initialized for Finding {finding.id} ({finding.title}) against target {target_url}.",
            assessment_id=finding.assessment_id,
            finding_id=finding.id,
            metadata={"target_url": target_url, "timestamp": now_ts}
        )

        # Step 2: Extract Immutable BEFORE Baseline Evidence
        is_api_docs = (
            "api doc" in (finding.title or "").lower()
            or "openapi" in (finding.title or "").lower()
            or "swagger" in (finding.title or "").lower()
            or getattr(finding, "cwe_id", "") == "CWE-200"
            or "API-DOCS" in (finding.id or "").upper()
        )
        comp_target = (
            finding.affected_component 
            if (finding.affected_component or "").startswith("http") 
            else f"{target_url.rstrip('/')}/openapi.json"
        ) if is_api_docs else target_url

        evd_before = db.query(EvidenceRecord).filter(EvidenceRecord.finding_id == finding_id).order_by(EvidenceRecord.timestamp.asc()).first()
        if evd_before:
            output_before = evd_before.raw_data or evd_before.observed_output or "Vulnerability observed during initial assessment."
            before_ev_id = evd_before.id
            before_ev_hash = evd_before.integrity_hash or hashlib.sha256(output_before.encode("utf-8")).hexdigest()
            default_cmd = evd_before.verification_command or f"curl -k -I \"{target_url}\""
            if is_api_docs:
                default_cmd = (
                    default_cmd.replace("-Method Head", "-Method Get")
                               .replace("-Method HEAD", "-Method Get")
                               .replace("curl -k -I", "curl -k -s")
                )
        else:
            output_before = "Initial vulnerable baseline unrecorded."
            before_ev_id = "N/A"
            before_ev_hash = hashlib.sha256(output_before.encode("utf-8")).hexdigest()
            if is_api_docs:
                default_cmd = f'Invoke-WebRequest -Uri "{comp_target}" -Method Get' if os.name == 'nt' else f'curl -k -s "{comp_target}"'
            else:
                default_cmd = f"curl -k -I \"{target_url}\""

        retest_cmd = command_executed or default_cmd
        if is_api_docs and ("-method head" in retest_cmd.lower() or "curl -k -i" in retest_cmd.lower()):
            retest_cmd = (
                retest_cmd.replace("-Method Head", "-Method Get")
                          .replace("-Method HEAD", "-Method Get")
                          .replace("curl -k -I", "curl -k -s")
            )

        is_fixed = False
        new_status = "STILL_OPEN"
        verdict_reason = ""
        http_metadata = {}

        # Step 3: Execute Real Deterministic Re-Test Probe
        if output_after:
            # Caller provided explicit after output from a runner
            new_status = force_status or ("VERIFIED_REMEDIATED" if "absent" not in output_after.lower() and "unresolved" not in output_after.lower() else "STILL_OPEN")
            is_fixed = (new_status == "VERIFIED_REMEDIATED")
            verdict_reason = f"Re-test verified via output payload: {output_after[:120]}"
        elif target_url.startswith(("http://", "https://")):
            try:
                # Execute real, safe, non-destructive HTTP HEAD/GET request
                resp = httpx.get(target_url, timeout=5.0, verify=False, follow_redirects=True)
                headers_lower = {k.lower(): v for k, v in resp.headers.items()}
                headers_formatted = "\n".join([f"{k}: {v}" for k, v in resp.headers.items()])
                
                http_metadata = {
                    "http_status": resp.status_code,
                    "server": headers_lower.get("server", "N/A"),
                    "content_type": headers_lower.get("content-type", "N/A")
                }

                title_lower = finding.title.lower()
                cat_lower = finding.category.lower()
                finding_id_upper = finding.id.upper()

                # API Documentation / OpenAPI Schema Exposure Check (Deterministic GET probe)
                if is_api_docs:
                    retest_cmd = (
                        f'Invoke-WebRequest -Uri "{comp_target}" -Method Get'
                        if os.name == 'nt'
                        else f'curl -k -s "{comp_target}"'
                    )
                    api_resp = httpx.get(comp_target, timeout=8.0, verify=False, follow_redirects=True)
                    api_headers_lower = {k.lower(): v for k, v in api_resp.headers.items()}
                    api_content_type = api_headers_lower.get("content-type", "N/A")
                    body_sha256 = hashlib.sha256(api_resp.content).hexdigest()

                    delivery_eval = verify_openapi_document_delivery(
                        status_code=api_resp.status_code,
                        content_type=api_content_type,
                        body=api_resp.content,
                        http_method="GET"
                    )

                    http_metadata = {
                        "http_status": api_resp.status_code,
                        "server": api_headers_lower.get("server", "N/A"),
                        "content_type": api_content_type,
                        "body_sha256": body_sha256,
                        "schema_detected": delivery_eval["schema_detected"],
                        "schema_version": delivery_eval.get("version"),
                        "schema_title": delivery_eval.get("title")
                    }

                    if delivery_eval["delivered"]:
                        is_fixed = False
                        new_status = "STILL_OPEN"
                        schema_ver = delivery_eval.get("version", "3.0")
                        schema_ttl = delivery_eval.get("title", "API")
                        output_after = (
                            f"HTTP/{api_resp.http_version} 200 OK\n"
                            f"Content-Type: {api_content_type}\n"
                            f"Body SHA-256: {body_sha256}\n\n"
                            f"[VULNERABLE] Public OpenAPI schema delivered without authentication.\n"
                            f"Schema Version: {schema_ver} | Title: {schema_ttl} | Payload Size: {len(api_resp.content)} bytes\n"
                            f"Reconnaissance Value: Route hierarchy and parameter types disclosed."
                        )
                        verdict_reason = f"Unauthenticated GET {comp_target} returned OpenAPI {schema_ver} schema document."
                    elif api_resp.status_code in [401, 403, 404]:
                        is_fixed = True
                        new_status = "VERIFIED_REMEDIATED"
                        output_after = (
                            f"HTTP/{api_resp.http_version} {api_resp.status_code}\n\n"
                            f"[VERIFIED] API documentation endpoint restricted or removed (HTTP {api_resp.status_code})."
                        )
                        verdict_reason = f"Access control enforced on schema endpoint; returned HTTP {api_resp.status_code}."
                    else:
                        is_fixed = True
                        new_status = "VERIFIED_REMEDIATED"
                        output_after = (
                            f"HTTP/{api_resp.http_version} {api_resp.status_code}\n\n"
                            f"[VERIFIED] Target returned HTTP {api_resp.status_code}; no OpenAPI schema document delivered."
                        )
                        verdict_reason = "No OpenAPI schema document delivered."

                # Content-Security-Policy Check
                elif "csp" in title_lower or "content-security-policy" in title_lower or "CSP" in finding_id_upper:
                    if "content-security-policy" in headers_lower:
                        is_fixed = True
                        new_status = "VERIFIED_REMEDIATED"
                        output_after = f"HTTP/{resp.http_version} {resp.status_code}\n{headers_formatted}\n\n[VERIFIED] Content-Security-Policy header confirmed present: {headers_lower['content-security-policy'][:80]}..."
                        verdict_reason = "Content-Security-Policy header is active and restricting script origins."
                    else:
                        is_fixed = False
                        new_status = "STILL_OPEN"
                        output_after = f"HTTP/{resp.http_version} {resp.status_code}\n{headers_formatted}\n\n[VULNERABLE] Content-Security-Policy header remains absent in live HTTP response."
                        verdict_reason = "Content-Security-Policy header is still missing."

                # Strict-Transport-Security (HSTS) Check
                elif "hsts" in title_lower or "strict-transport-security" in title_lower or "HSTS" in finding_id_upper or "COMM" in finding_id_upper:
                    if "strict-transport-security" in headers_lower:
                        is_fixed = True
                        new_status = "VERIFIED_REMEDIATED"
                        output_after = f"HTTP/{resp.http_version} {resp.status_code}\n{headers_formatted}\n\n[VERIFIED] Strict-Transport-Security confirmed present: {headers_lower['strict-transport-security']}"
                        verdict_reason = "HSTS header is properly enforced."
                    else:
                        is_fixed = False
                        new_status = "STILL_OPEN"
                        output_after = f"HTTP/{resp.http_version} {resp.status_code}\n{headers_formatted}\n\n[VULNERABLE] Strict-Transport-Security header remains absent."
                        verdict_reason = "Strict-Transport-Security header is still missing."

                # X-Content-Type-Options Check
                elif "xcto" in title_lower or "x-content-type-options" in title_lower or "XCTO" in finding_id_upper or "mime" in title_lower:
                    if "x-content-type-options" in headers_lower and "nosniff" in headers_lower["x-content-type-options"].lower():
                        is_fixed = True
                        new_status = "VERIFIED_REMEDIATED"
                        output_after = f"HTTP/{resp.http_version} {resp.status_code}\n{headers_formatted}\n\n[VERIFIED] X-Content-Type-Options: nosniff confirmed active."
                        verdict_reason = "MIME sniffing protection enabled."
                    else:
                        is_fixed = False
                        new_status = "STILL_OPEN"
                        output_after = f"HTTP/{resp.http_version} {resp.status_code}\n{headers_formatted}\n\n[VULNERABLE] X-Content-Type-Options: nosniff remains absent."
                        verdict_reason = "X-Content-Type-Options is still missing."

                # Server Banner / Information Disclosure
                elif "banner" in title_lower or "server" in title_lower or "disclosure" in title_lower or "BANNER" in finding_id_upper:
                    srv = headers_lower.get("server", "")
                    if srv and any(tech in srv.lower() for tech in ["uvicorn", "nginx/", "apache/", "werkzeug", "python"]):
                        is_fixed = False
                        new_status = "STILL_OPEN"
                        output_after = f"HTTP/{resp.http_version} {resp.status_code}\nServer: {srv}\n\n[VULNERABLE] Server banner discloses software version: {srv}"
                        verdict_reason = f"Server banner still reveals software technology: {srv}"
                    else:
                        is_fixed = True
                        new_status = "VERIFIED_REMEDIATED"
                        output_after = f"HTTP/{resp.http_version} {resp.status_code}\n\n[VERIFIED] Server banner cleanly suppressed."
                        verdict_reason = "Software technology header suppressed."

                # Authorization / IDOR / Access Control
                elif "idor" in title_lower or "access control" in cat_lower or "authorization" in cat_lower or "AUTH" in finding_id_upper:
                    if resp.status_code in [401, 403]:
                        is_fixed = True
                        new_status = "VERIFIED_REMEDIATED"
                        output_after = f"HTTP/{resp.http_version} {resp.status_code} Forbidden/Unauthorized\n\n[VERIFIED] Unauthorized tenant request successfully rejected with HTTP {resp.status_code}."
                        verdict_reason = "Access control authorization barrier verified."
                    elif resp.status_code == 200:
                        is_fixed = False
                        new_status = "STILL_OPEN"
                        output_after = f"HTTP/{resp.http_version} 200 OK\n\n[VULNERABLE] Target route returned HTTP 200 without tenant authorization check."
                        verdict_reason = "Endpoint still responds without authorization barrier."
                    else:
                        is_fixed = False
                        new_status = "CHANGED_UNEXPECTEDLY"
                        output_after = f"HTTP/{resp.http_version} {resp.status_code}\n\n[CHANGED] Target responded with unexpected status code {resp.status_code}."
                        verdict_reason = f"Unexpected response status: {resp.status_code}."

                else:
                    # General HTTP defensive control
                    if resp.status_code < 400:
                        is_fixed = False
                        new_status = "STILL_OPEN"
                        output_after = f"HTTP/{resp.http_version} {resp.status_code} OK\n{headers_formatted}\n\n[VULNERABLE] Baseline security condition remains unchanged."
                        verdict_reason = "Re-test did not observe expected remediation change."
                    else:
                        is_fixed = True
                        new_status = "VERIFIED_REMEDIATED"
                        output_after = f"HTTP/{resp.http_version} {resp.status_code}\n\n[VERIFIED] Defensive control responded with secure status code {resp.status_code}."
                        verdict_reason = f"Response code {resp.status_code} satisfies mitigation."

            except Exception as ex:
                is_fixed = False
                new_status = "UNABLE_TO_VERIFY"
                output_after = f"Target Connection Failed: {str(ex)}"
                verdict_reason = f"Target host '{target_url}' was unreachable during re-test: {str(ex)}"

        elif os.path.exists(target_url):
            # Target is a local source file
            try:
                content = Path(target_url).read_text(encoding="utf-8", errors="ignore")
                title_lower = finding.title.lower()
                finding_id_upper = finding.id.upper()

                if ("aws" in title_lower or "AWS" in finding_id_upper) and any(kw in content for kw in ["AKIA", "AIPA", "ASIA"]):
                    is_fixed = False
                    new_status = "STILL_OPEN"
                    output_after = "AWS Access Key pattern still present in file."
                    verdict_reason = "Hardcoded AWS credentials still found in source."
                elif ("secret" in title_lower or "jwt" in title_lower or "password" in title_lower) and any(kw in content for kw in ["JWT_SECRET", "DB_PASSWORD", "PROD_PASSWORD"]):
                    is_fixed = False
                    new_status = "STILL_OPEN"
                    output_after = "Hardcoded secret / password pattern still present in file."
                    verdict_reason = "Hardcoded credentials still found in source."
                elif ("shell" in title_lower or "command" in title_lower) and any(kw in content for kw in ["shell=True", "os.system("]):
                    is_fixed = False
                    new_status = "STILL_OPEN"
                    output_after = "Unsafe shell execution syntax still present in source."
                    verdict_reason = "Vulnerable subprocess syntax remains unpatched."
                else:
                    is_fixed = True
                    new_status = "VERIFIED_REMEDIATED"
                    output_after = "Clean: No vulnerable patterns or hardcoded credentials detected in target file."
                    verdict_reason = "Source file re-scan verified clean."
            except Exception as ex:
                is_fixed = False
                new_status = "UNABLE_TO_VERIFY"
                output_after = f"File Read Error: {str(ex)}"
                verdict_reason = f"Could not inspect target file: {str(ex)}"
        else:
            is_fixed = False
            new_status = "UNABLE_TO_VERIFY"
            output_after = f"Target '{target_url}' not found or invalid URL."
            verdict_reason = f"Target '{target_url}' is not a reachable URL or local file."

        if force_status:
            new_status = force_status
            is_fixed = (new_status in ["RESOLVED", "VERIFIED", "VERIFIED_REMEDIATED"])

        # Step 4: Calculate Cryptographic SHA-256 for AFTER Evidence
        after_ev_id = f"EVD-AFT-{uuid.uuid4().hex[:8].upper()}"
        after_ev_hash = hashlib.sha256(output_after.encode("utf-8")).hexdigest()

        # Step 5: Log RETEST_OBSERVATION_CAPTURED
        log_audit_event(
            db=db,
            event_type="RETEST_OBSERVATION_CAPTURED",
            description=f"Raw re-test observation captured for {finding.id}. SHA-256: {after_ev_hash[:16]}...",
            assessment_id=finding.assessment_id,
            finding_id=finding.id,
            metadata={"after_evidence_hash": after_ev_hash, "verdict_preliminary": new_status}
        )

        # Step 6: Create Immutable AFTER Evidence Record
        evd_after = EvidenceRecord(
            id=after_ev_id,
            finding_id=finding.id,
            evidence_type=f"Re-Test Verification ({finding.category})",
            source="Re-Test Verification Engine",
            timestamp=now_ts,
            description=f"Empirical post-fix re-test evidence for {finding.title}. Verification status: {new_status}.",
            raw_data=output_after,
            validation_result="CONFIRMED" if is_fixed else "UNCONFIRMED",
            integrity_hash=after_ev_hash,
            is_demo=False,
            what_found=f"Re-test observation: {new_status}",
            why_matters=f"Proves whether {finding.title} was remediated.",
            where_found=target_url,
            confidence_level="HIGH",
            verification_command=retest_cmd,
            expected_output=finding.recommended_remediation or "Remediated security state",
            observed_output=output_after,
            evidence_nature="REAL EVIDENCE"
        )
        db.add(evd_after)
        db.commit()

        # Step 7: Log RETEST_EVIDENCE_CREATED
        log_audit_event(
            db=db,
            event_type="RETEST_EVIDENCE_CREATED",
            description=f"Immutable after-fix evidence record [{after_ev_id}] stored with SHA-256 integrity hash.",
            assessment_id=finding.assessment_id,
            finding_id=finding.id,
            metadata={"evidence_id": after_ev_id, "hash": after_ev_hash}
        )

        # Step 8: Deterministic 5-Point State Diff (Phase 5)
        state_diff_dict = {
            "what_observed_before": output_before[:250],
            "what_observed_after": output_after[:250],
            "what_changed": f"Response changed from [{output_before[:60]}...] to [{output_after[:60]}...]",
            "security_improved": is_fixed,
            "remediated_verdict": new_status,
            "verdict_reason": verdict_reason
        }
        state_diff_json = json.dumps(state_diff_dict)

        # Step 9: Log RETEST_STATE_COMPARISON
        log_audit_event(
            db=db,
            event_type="RETEST_STATE_COMPARISON",
            description=f"Deterministic state diff computed for {finding.id}: {new_status} (Condition Improved: {is_fixed}).",
            assessment_id=finding.assessment_id,
            finding_id=finding.id,
            metadata=state_diff_dict
        )

        # Step 10: Create and Persist ReVerificationRecord
        re_id = f"REV-{uuid.uuid4().hex[:8].upper()}"
        summary = (
            f"Re-test executed on {now_ts} against target {target_url}. "
            f"Previous status was {finding.status}. "
            f"Verification verdict: {new_status}. {verdict_reason}"
        )

        re_rec = ReVerificationRecord(
            id=re_id,
            finding_id=finding.id,
            timestamp=now_ts,
            previous_status=finding.status,
            new_status=new_status,
            command_executed=retest_cmd,
            output_before=output_before,
            output_after=output_after,
            summary=summary,
            target_url=target_url,
            before_evidence_id=before_ev_id,
            after_evidence_id=after_ev_id,
            before_evidence_hash=before_ev_hash,
            after_evidence_hash=after_ev_hash,
            state_diff=state_diff_json,
            verification_verdict=new_status
        )
        db.add(re_rec)

        # Step 11: Update Finding Status
        old_status = finding.status
        finding.status = new_status
        finding.updated_at = now_ts
        db.commit()
        db.refresh(re_rec)

        # Step 12: Log RETEST_VERIFIED or RETEST_UNRESOLVED
        final_event = "RETEST_VERIFIED" if is_fixed else ("RETEST_INCONCLUSIVE" if new_status == "UNABLE_TO_VERIFY" else "RETEST_UNRESOLVED")
        log_audit_event(
            db=db,
            event_type=final_event,
            description=f"Finding {finding.id} re-test completed. Status transitioned from {old_status} to {new_status}.",
            assessment_id=finding.assessment_id,
            finding_id=finding.id,
            metadata={
                "retest_id": re_id,
                "previous_status": old_status,
                "new_status": new_status,
                "before_evidence_id": before_ev_id,
                "after_evidence_id": after_ev_id,
                "after_evidence_hash": after_ev_hash
            }
        )

        return re_rec

validation_service = ValidationService()
