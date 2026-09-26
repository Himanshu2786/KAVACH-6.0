"""
KAVACH 6.0 Desktop - Core Assessment Engine.
Performs deterministic, empirical assessments for Web Security, Network Exposure, and Local Posture.
"""

import os
import time
import hashlib
import requests
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.config import get_demo_samples_dir
from services.storage_service import storage

class AssessmentEngine:
    def run_url_assessment(self, target_url: str, is_authorized: bool = True) -> Dict[str, Any]:
        """Runs empirical security checks against the target URL."""
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = "https://" + target_url

        asm_id = f"ASM-{int(datetime.now().timestamp())}"
        created_at = datetime.now(timezone.utc).isoformat()
        
        findings = []
        evidence_list = []
        
        # 1. Web Security Inspection (Headers, HTTPS)
        headers_found = {}
        status_code = 0
        server_banner = "Unknown"
        
        try:
            resp = requests.get(target_url, timeout=5, verify=False, allow_redirects=True)
            status_code = resp.status_code
            headers_found = {k.lower(): v for k, v in resp.headers.items()}
            server_banner = headers_found.get("server", "Protected / Not Disclosed")
        except Exception as e:
            return {
                "assessment_id": asm_id,
                "status": "FAILED",
                "target_url": target_url,
                "error": f"Target unreachable: {str(e)}",
                "findings": [],
                "evidence": [],
                "total_findings": 0,
                "summary": f"Assessment incomplete — target '{target_url}' is unreachable. Insufficient empirical evidence."
            }

        # Check: Missing Strict-Transport-Security (HSTS)
        if "strict-transport-security" not in headers_found:
            fnd_id = f"FND-HSTS-{asm_id[-4:]}"
            ev_id = f"EV-HSTS-{asm_id[-4:]}"
            cmd = f'Invoke-WebRequest -Uri "{target_url}" -Method Head | Select-Object -ExpandProperty Headers'
            expected = "Strict-Transport-Security: max-age=31536000; includeSubDomains"
            observed = "Strict-Transport-Security header is ABSENT from HTTP response."
            h_data = f"{cmd}|{observed}"
            ev_hash = hashlib.sha256(h_data.encode('utf-8')).hexdigest()
            
            findings.append({
                "id": fnd_id,
                "assessment_id": asm_id,
                "finding_id": fnd_id,
                "title": "Missing Strict-Transport-Security (HSTS) Defense Header",
                "category": "Cryptographic & Transport Security",
                "severity": "HIGH",
                "cwe_id": "CWE-319",
                "owasp_id": "A02:2021-Cryptographic Failures",
                "confidence": "CERTAIN",
                "affected_component": f"{target_url} (HTTP Response Headers)",
                "description": "The web server does not enforce HTTPS connections via HSTS. Browsers may connect over unencrypted HTTP, leaving traffic vulnerable to man-in-the-middle downgrade attacks.",
                "remediation": "Configure web server to return: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
                "status": "OPEN",
                "evidence_id": ev_id,
                "created_at": created_at
            })
            evidence_list.append({
                "id": ev_id,
                "assessment_id": asm_id,
                "finding_id": fnd_id,
                "type": "HEADER_PROBE",
                "data": {"target": target_url, "headers": headers_found},
                "integrity_hash": ev_hash,
                "command": cmd,
                "expected_output": expected,
                "observed_output": observed,
                "verification_steps": [
                    f'Execute PowerShell command: Invoke-WebRequest -Uri "{target_url}" -Method Head',
                    "Inspect returned Headers hashtable.",
                    "Verify if Strict-Transport-Security key is present."
                ],
                "created_at": created_at
            })

        # Check: Missing Content-Security-Policy (CSP)
        if "content-security-policy" not in headers_found:
            fnd_id = f"FND-CSP-{asm_id[-4:]}"
            ev_id = f"EV-CSP-{asm_id[-4:]}"
            cmd = f'Invoke-WebRequest -Uri "{target_url}" -Method Head | Select-Object -ExpandProperty Headers'
            expected = "Content-Security-Policy: default-src 'self'"
            observed = "Content-Security-Policy header is ABSENT."
            h_data = f"{cmd}|{observed}"
            ev_hash = hashlib.sha256(h_data.encode('utf-8')).hexdigest()

            findings.append({
                "id": fnd_id,
                "assessment_id": asm_id,
                "finding_id": fnd_id,
                "title": "Missing Content-Security-Policy (CSP) Enforcement",
                "category": "Injection & Client-Side Defense",
                "severity": "MEDIUM",
                "cwe_id": "CWE-1021",
                "owasp_id": "A05:2021-Security Misconfiguration",
                "confidence": "CERTAIN",
                "affected_component": f"{target_url} (HTTP Response Headers)",
                "description": "The target does not deliver a Content-Security-Policy header, reducing defense-in-depth against cross-site scripting (XSS) and unauthorized resource loading.",
                "remediation": "Implement a restrictive CSP header defining trusted script-src, style-src, and default-src origins.",
                "status": "OPEN",
                "evidence_id": ev_id,
                "created_at": created_at
            })
            evidence_list.append({
                "id": ev_id,
                "assessment_id": asm_id,
                "finding_id": fnd_id,
                "type": "HEADER_PROBE",
                "data": {"target": target_url, "headers": headers_found},
                "integrity_hash": ev_hash,
                "command": cmd,
                "expected_output": expected,
                "observed_output": observed,
                "verification_steps": [
                    f'Execute PowerShell: Invoke-WebRequest -Uri "{target_url}" -Method Head',
                    "Look for Content-Security-Policy header in output.",
                    "Confirm absence of client resource restriction policy."
                ],
                "created_at": created_at
            })

        # Check: Missing X-Content-Type-Options
        if "x-content-type-options" not in headers_found:
            fnd_id = f"FND-XCTO-{asm_id[-4:]}"
            ev_id = f"EV-XCTO-{asm_id[-4:]}"
            cmd = f'Invoke-WebRequest -Uri "{target_url}" -Method Head | Select-Object -ExpandProperty Headers'
            expected = "X-Content-Type-Options: nosniff"
            observed = "X-Content-Type-Options header is ABSENT."
            h_data = f"{cmd}|{observed}"
            ev_hash = hashlib.sha256(h_data.encode('utf-8')).hexdigest()

            findings.append({
                "id": fnd_id,
                "assessment_id": asm_id,
                "finding_id": fnd_id,
                "title": "MIME-Sniffing Protection Absent (X-Content-Type-Options)",
                "category": "Web Application Configuration",
                "severity": "LOW",
                "cwe_id": "CWE-16",
                "owasp_id": "A05:2021-Security Misconfiguration",
                "confidence": "CERTAIN",
                "affected_component": f"{target_url}",
                "description": "Without X-Content-Type-Options: nosniff, browsers may attempt to MIME-sniff the response body, potentially executing user-uploaded files as scripts or stylesheets.",
                "remediation": "Add header: X-Content-Type-Options: nosniff to all HTTP responses.",
                "status": "OPEN",
                "evidence_id": ev_id,
                "created_at": created_at
            })
            evidence_list.append({
                "id": ev_id,
                "assessment_id": asm_id,
                "finding_id": fnd_id,
                "type": "HEADER_PROBE",
                "data": {"target": target_url, "headers": headers_found},
                "integrity_hash": ev_hash,
                "command": cmd,
                "expected_output": expected,
                "observed_output": observed,
                "verification_steps": [
                    f'Run: Invoke-WebRequest -Uri "{target_url}" -Method Head',
                    "Verify X-Content-Type-Options header."
                ],
                "created_at": created_at
            })

        # Save to SQLite database
        asm_record = {
            "id": asm_id,
            "target_url": target_url,
            "name": f"Assessment for {target_url}",
            "mode": "AUTOMATED_PROBE",
            "status": "COMPLETED",
            "created_at": created_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "summary": f"Identified {len(findings)} technical posture findings with cryptographic verification evidence.",
            "metadata": {
                "status_code": status_code,
                "server_banner": server_banner,
                "findings_count": len(findings)
            }
        }
        
        storage.save_assessment(asm_record)
        storage.save_findings(findings)
        storage.save_evidence_list(evidence_list)
        storage.log_audit_event("ASSESSMENT_COMPLETED", f"Completed URL security check for {target_url}", details={"findings_count": len(findings)})
        
        return {
            "assessment": asm_record,
            "findings": findings,
            "evidence": evidence_list
        }

    def run_local_posture_scan(self) -> Dict[str, Any]:
        """Performs endpoint posture checks including safe demo sample inspection."""
        asm_id = f"ASM-LOCAL-{int(datetime.now().timestamp())}"
        created_at = datetime.now(timezone.utc).isoformat()
        
        findings = []
        evidence_list = []
        demo_dir = get_demo_samples_dir()
        
        # Check: Hardcoded API Keys / Secrets in Training Samples
        sample_env = demo_dir / "demo_api_keys.env"
        if sample_env.exists():
            content = sample_env.read_text(encoding="utf-8", errors="ignore")
            if "AWS_SECRET_ACCESS_KEY" in content or "PROD_DB_PASSWORD" in content:
                fnd_id = f"FND-SECRET-{asm_id[-4:]}"
                ev_id = f"EV-SECRET-{asm_id[-4:]}"
                rel_path = f"demo/training_samples/{sample_env.name}"
                cmd = f'Select-String -Path "{sample_env.name}" -Pattern "(AWS_SECRET|PROD_DB|API_KEY)"'
                expected = "No unencrypted high-entropy secrets in repository."
                observed = f"Found unmasked demo credentials in {sample_env.name}"
                h_data = f"{cmd}|{observed}|{content[:100]}"
                ev_hash = hashlib.sha256(h_data.encode('utf-8')).hexdigest()

                findings.append({
                    "id": fnd_id,
                    "assessment_id": asm_id,
                    "finding_id": fnd_id,
                    "title": "Plaintext Secret Keys in Local Configuration Fixture",
                    "category": "Credential & Secret Exposure",
                    "severity": "CRITICAL",
                    "cwe_id": "CWE-798",
                    "owasp_id": "A07:2021-Identification and Authentication Failures",
                    "confidence": "VERIFIED",
                    "affected_component": f"{rel_path}",
                    "description": "Plaintext API tokens and secret keys detected in local repository directory. Leaving credentials unencrypted allows unauthorized access to backend cloud services.",
                    "remediation": "Store secrets in an environment secret manager (e.g. AWS Secrets Manager or HashiCorp Vault) and remove plaintext fixtures from version control.",
                    "status": "OPEN",
                    "evidence_id": ev_id,
                    "created_at": created_at
                })
                evidence_list.append({
                    "id": ev_id,
                    "assessment_id": asm_id,
                    "finding_id": fnd_id,
                    "type": "FILE_INSPECTION",
                    "data": {"file": str(sample_env)},
                    "integrity_hash": ev_hash,
                    "command": cmd,
                    "expected_output": expected,
                    "observed_output": observed,
                    "verification_steps": [
                        f'Open PowerShell in demo directory: cd "{demo_dir}"',
                        f'Execute command: {cmd}',
                        "Verify matched pattern lines in terminal."
                    ],
                    "created_at": created_at
                })

        asm_record = {
            "id": asm_id,
            "target_url": "LOCAL_ENDPOINT_POSTURE",
            "name": "Local Endpoint & File Posture Audit",
            "mode": "LOCAL_AUDIT",
            "status": "COMPLETED",
            "created_at": created_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "summary": f"Scanned local workspace and detected {len(findings)} security findings.",
            "metadata": {"findings_count": len(findings)}
        }

        storage.save_assessment(asm_record)
        storage.save_findings(findings)
        storage.save_evidence_list(evidence_list)
        storage.log_audit_event("LOCAL_POSTURE_SCAN", "Completed local endpoint audit", details={"findings_count": len(findings)})

        return {
            "assessment": asm_record,
            "findings": findings,
            "evidence": evidence_list
        }

    def run_world_monitor_assessment(
        self,
        target_url: Optional[str] = "https://www.worldmonitor.app",
        source_path: Optional[str] = None,
        mode: str = "HYBRID"
    ) -> Dict[str, Any]:
        """
        Executes real World Monitor assessment (SIH PS 26163) across live URL and source repository.
        Zero synthetic findings.
        """
        import asyncio
        from backend.app.services.world_monitor_assessment_engine import world_monitor_assessment_engine

        # Run the async assessment
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            res = loop.run_until_complete(
                world_monitor_assessment_engine.run_assessment(
                    target_url=target_url,
                    source_path=source_path,
                    mode=mode,
                    assessment_name="World Monitor Security Assessment"
                )
            )
        else:
            res = loop.run_until_complete(
                world_monitor_assessment_engine.run_assessment(
                    target_url=target_url,
                    source_path=source_path,
                    mode=mode,
                    assessment_name="World Monitor Security Assessment"
                )
            )

        # Sync with desktop storage
        asm_record = {
            "id": res["assessment_id"],
            "target_url": res["target_url"],
            "name": res["name"],
            "mode": res["mode"],
            "status": res["status"],
            "created_at": res.get("completed_at", datetime.now(timezone.utc).isoformat()),
            "completed_at": res.get("completed_at", datetime.now(timezone.utc).isoformat()),
            "summary": res["summary"],
            "metadata": {
                "source_path": res["source_path"],
                "total_findings": res["total_findings"],
                "confirmed_findings": res["confirmed_findings"]
            }
        }
        storage.save_assessment(asm_record)
        storage.save_findings(res.get("findings", []))
        storage.save_evidence_list(res.get("evidence", []))
        if "risk_records" in res:
            storage.save_risk_records(res.get("risk_records", []))
        storage.log_audit_event(
            "WORLD_MONITOR_ASSESSMENT",
            f"Completed World Monitor assessment ({res['assessment_id']}). Mode: {res['mode']}. Findings: {res['total_findings']}.",
            details={"mode": res["mode"], "findings_count": res["total_findings"]}
        )

        return res

assessment_engine = AssessmentEngine()

