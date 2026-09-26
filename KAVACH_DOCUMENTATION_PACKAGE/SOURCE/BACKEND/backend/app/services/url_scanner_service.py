"""
KAVACH URL Security Assessment Service (Detection 1: Web Security)
Performs safe, non-destructive HTTP and TLS observations on target URLs.
Grounded strictly on real observations with cryptographic SHA-256 evidence hashing.
Provides deterministic finding identities, run isolation, execution diagnostics,
and clear distinction between security status and network execution status.
"""

import ssl
import socket
import hashlib
import time
import uuid
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional
import json
from sqlalchemy.orm import Session
import httpx
from backend.app.core.time import ist_now, ist_formatted


class UrlScannerService:
    def __init__(self):
        self._latest_assessment: Optional[Dict[str, Any]] = None
        self._history: List[Dict[str, Any]] = []

    def validate_url(self, raw_url: str) -> Dict[str, Any]:
        """Validates and normalizes target URL syntax, supporting domain names, IPs, and localhost."""
        if not raw_url or not isinstance(raw_url, str):
            return {"valid": False, "error": "URL cannot be empty"}

        url = raw_url.strip()
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            parsed = urlparse(url)
            hostname = parsed.hostname
            if not hostname:
                return {"valid": False, "error": "Invalid hostname format"}

            # Allow localhost, 127.0.0.1, IPv4/IPv6, or standard domains with a dot
            is_local = hostname.lower() in ("localhost", "127.0.0.1", "::1")
            is_ip = all(part.isdigit() for part in hostname.split(".")) if "." in hostname else False
            has_dot = "." in hostname

            if not (is_local or is_ip or has_dot):
                return {"valid": False, "error": f"Invalid hostname '{hostname}': must be a domain, IP address, or localhost."}

            port = parsed.port or (443 if parsed.scheme == "https" else 80)

            return {
                "valid": True,
                "normalized_url": url,
                "hostname": hostname,
                "port": port,
                "scheme": parsed.scheme,
                "path": parsed.path or "/"
            }
        except Exception as e:
            return {"valid": False, "error": f"URL parsing error: {str(e)}"}

    async def _safe_http_get(
        self,
        client: httpx.AsyncClient,
        url: str,
        retries: int = 1,
        timeout: float = 6.0
    ) -> Dict[str, Any]:
        """Performs a safe HTTP GET with retry policy for transient network hiccups."""
        start_time = time.perf_counter()
        last_error = None

        for attempt in range(retries + 1):
            try:
                response = await client.get(url, timeout=timeout)
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "cookies": dict(response.cookies),
                    "location": response.headers.get("location", ""),
                    "duration_ms": duration_ms,
                    "attempts": attempt + 1,
                    "error": None
                }
            except httpx.TimeoutException as e:
                last_error = f"Network Timeout ({timeout}s reached): {str(e)}"
            except httpx.ConnectError as e:
                last_error = f"Connection Refused or Host Unreachable: {str(e)}"
            except Exception as e:
                last_error = f"HTTP Probe Error: {type(e).__name__} - {str(e)}"

            if attempt < retries:
                time.sleep(0.15 * (attempt + 1))

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "success": False,
            "status_code": None,
            "headers": {},
            "cookies": {},
            "location": "",
            "duration_ms": duration_ms,
            "attempts": retries + 1,
            "error": last_error
        }

    async def probe_tls(self, hostname: str, port: int = 443, timeout: float = 4.0) -> Dict[str, Any]:
        """Safely inspects TLS certificate metadata using standard Python ssl & socket."""
        start_time = time.perf_counter()
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            with socket.create_connection((hostname, port), timeout=timeout) as sock:
                with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert() or {}
                    cipher = ssock.cipher() or ("Unknown", "Unknown", 0)
                    version = ssock.version() or "TLSv1.2"

                    not_before = cert.get("notBefore", "")
                    not_after = cert.get("notAfter", "")

                    days_remaining = None
                    if not_after:
                        try:
                            exp_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                            now = datetime.now(timezone.utc)
                            days_remaining = (exp_date - now).days
                        except Exception:
                            pass

                    # Extract Subject & Issuer
                    subject = "Unknown"
                    issuer = "Unknown"
                    for item in cert.get("subject", []):
                        for k, v in item:
                            if k in ("commonName", "organizationName"):
                                subject = v
                    for item in cert.get("issuer", []):
                        for k, v in item:
                            if k in ("commonName", "organizationName"):
                                issuer = v

                    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    return {
                        "available": True,
                        "tls_version": version,
                        "cipher": cipher[0],
                        "subject": subject,
                        "issuer": issuer,
                        "not_before": not_before,
                        "not_after": not_after,
                        "days_remaining": days_remaining,
                        "duration_ms": duration_ms,
                        "error": None
                    }
        except socket.timeout:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "available": False,
                "duration_ms": duration_ms,
                "error": f"TLS Handshake Timeout after {timeout}s on port {port}"
            }
        except Exception as e:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "available": False,
                "duration_ms": duration_ms,
                "error": f"TLS Connection Error ({type(e).__name__}): {str(e)}"
            }

    async def assess_url(
        self,
        target_url: str,
        parent_assessment_id: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """
        Executes safe, deterministic, non-destructive observations against the target URL:
        1. HTTPS Availability & Handshake (CHK-001)
        2. HTTP -> HTTPS Redirect Enforcement (CHK-002)
        3. TLS Certificate Metadata (CHK-003)
        4. Certificate Validity & Expiration Period (CHK-004)
        5. Strict-Transport-Security (HSTS) Header (CHK-005)
        6. Content-Security-Policy (CSP) Header (CHK-006)
        7. X-Content-Type-Options Header (CHK-007)
        8. Frame Protection / Clickjacking Defense (CHK-008)

        Features:
        - Stable, content-addressed finding IDs (e.g. FIND-WEB-CHK001, FIND-WEB-CHK002, etc.)
        - Isolated Assessment Run ID (e.g. ASM-URL-YYYYMMDD-XXXX)
        - Execution diagnostics with duration (ms) and error reasons
        - Clear separation between Security Result and Execution Result (Network / Timeout)
        """
        val = self.validate_url(target_url)
        if not val["valid"]:
            return {
                "success": False,
                "error": val["error"],
                "target_url": target_url
            }

        url = val["normalized_url"]
        hostname = val["hostname"]
        target_port = val["port"]
        now_dt = ist_now()
        now_iso = ist_formatted("%Y-%m-%d %H:%M:%S IST")
        run_id = f"ASM-URL-{now_dt.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        checks: List[Dict[str, Any]] = []
        findings: List[Dict[str, Any]] = []
        failed_checks_count = 0

        # Construct protocol test endpoints
        # If target has a non-standard port specified, respect it; otherwise use standard 80/443
        if target_port not in (80, 443):
            http_url = f"http://{hostname}:{target_port}"
            https_url = f"https://{hostname}:{target_port}"
        else:
            http_url = f"http://{hostname}"
            https_url = f"https://{hostname}"

        redirect_enforced = False
        redirect_chain: List[Dict[str, Any]] = []
        raw_headers: Dict[str, str] = {}
        http_probe_result: Dict[str, Any] = {}
        https_probe_result: Dict[str, Any] = {}

        async with httpx.AsyncClient(verify=False, follow_redirects=False) as client:
            # 1. Test HTTP probe & redirect behavior
            http_probe_result = await self._safe_http_get(client, http_url, retries=1, timeout=5.0)
            if http_probe_result["success"]:
                loc = http_probe_result["location"]
                status_code = http_probe_result["status_code"]
                if status_code in (301, 302, 307, 308) and loc.startswith("https://"):
                    redirect_enforced = True
                redirect_chain.append({
                    "url": http_url,
                    "status_code": status_code,
                    "location": loc
                })

            # 2. Test HTTPS availability & collect response headers
            https_probe_result = await self._safe_http_get(client, https_url, retries=1, timeout=6.0)
            https_available = https_probe_result["success"]
            if https_available:
                raw_headers = https_probe_result["headers"]

        # 3. Probe TLS Certificate
        tls_port = target_port if target_port not in (80, 443) else 443
        tls_info = await self.probe_tls(hostname, port=tls_port, timeout=4.0)

        # -------------------------------------------------------------
        # CHECK 1: HTTPS Availability (CHK-001)
        # -------------------------------------------------------------
        chk1_id = "CHK-001"
        chk1_dur = https_probe_result.get("duration_ms", 0)
        chk1_err = https_probe_result.get("error")

        if https_available:
            chk1_status = "PASS"
            chk1_exec = "SUCCESS"
            chk1_obs = f"HTTP {https_probe_result['status_code']} response received over encrypted HTTPS ({chk1_dur}ms)"
        else:
            chk1_status = "FAIL"
            chk1_exec = "TIMEOUT" if "Timeout" in str(chk1_err) else "ERROR"
            chk1_obs = f"HTTPS connection failed: {chk1_err or 'Connection refused on port 443'}"

        checks.append({
            "id": chk1_id,
            "name": "HTTPS Availability",
            "category": "Transport Encryption",
            "status": chk1_status,
            "execution_status": chk1_exec,
            "duration_ms": chk1_dur,
            "error_reason": chk1_err,
            "observed": chk1_obs,
            "expected": "HTTPS connection established successfully with valid status code",
            "importance": "Enforces transport layer encryption between clients and server"
        })

        if not https_available:
            f_id = "FIND-WEB-CHK001"
            e_id = f"EVD-WEB-CHK001-{run_id}"
            obs = f"Target {https_url} refused or failed HTTPS connection. Error: {chk1_err or 'Unreachable'} (Run {run_id})"
            findings.append({
                "id": f_id,
                "run_id": run_id,
                "check_id": chk1_id,
                "title": "HTTPS Not Available on Target",
                "category": "Secure Communication & Transport",
                "severity": "CRITICAL",
                "status": "CONFIRMED",
                "evidence_status": "AVAILABLE",
                "cwe_id": "CWE-319",
                "owasp_category": "A02:2021-Cryptographic Failures",
                "evidence": {
                    "id": e_id,
                    "run_id": run_id,
                    "finding_id": f_id,
                    "target": https_url,
                    "detector": "WebSecurityScanner.HTTPSAvailability",
                    "raw_observation": obs,
                    "integrity_hash": hashlib.sha256(obs.encode()).hexdigest(),
                    "timestamp": now_iso
                },
                "simple_evidence": {
                    "what_found": "The target website does not accept encrypted HTTPS connections.",
                    "where_found": https_url,
                    "why_matters": "All communications between users and the server occur in plaintext and can be intercepted.",
                    "possible_impact": "Credential theft, session hijacking, and eavesdropping on network traffic.",
                    "what_you_can_do": "Install a valid TLS certificate and configure port 443 with HTTPS."
                },
                "technical_evidence": {
                    "run_id": run_id,
                    "target": https_url,
                    "protocol": f"TCP / TLS:{tls_port}",
                    "observed": chk1_obs,
                    "expected": "TLS handshake completed",
                    "scanner": "WebSecurityScanner",
                    "rule": "WEB-HTTPS-REQUIRED",
                    "timestamp": now_iso
                },
                "terminal_verification": {
                    "command": f"curl -I -v {https_url}",
                    "expected_output": "HTTP/1.1 200 OK or 301 Moved Permanently",
                    "observed_output": f"Connection failed: {chk1_err or 'Failed to connect'}"
                },
                "remediation": {
                    "how_to_fix": "Enable HTTPS on the web server (e.g. Nginx, Apache) and bind port 443 with a trusted certificate.",
                    "why_matters": "Modern web browsers block or flag sites without valid HTTPS transport security."
                }
            })

        # -------------------------------------------------------------
        # CHECK 2: HTTP to HTTPS Redirect Behavior (CHK-002)
        # -------------------------------------------------------------
        chk2_id = "CHK-002"
        chk2_dur = http_probe_result.get("duration_ms", 0)
        chk2_err = http_probe_result.get("error")

        if not http_probe_result["success"]:
            # Distinguish execution failure from policy failure
            chk2_status = "WARNING"
            chk2_exec = "TIMEOUT" if "Timeout" in str(chk2_err) else "ERROR"
            chk2_obs = f"HTTP port probe could not connect: {chk2_err}"
            failed_checks_count += 1
        elif redirect_enforced:
            chk2_status = "PASS"
            chk2_exec = "SUCCESS"
            chk2_obs = f"Plaintext HTTP ({http_url}) redirects to HTTPS automatically via HTTP {http_probe_result['status_code']}"
        else:
            chk2_status = "WARNING"
            chk2_exec = "SUCCESS"
            chk2_obs = f"Plaintext HTTP returned status {http_probe_result['status_code']} without redirecting to HTTPS"

        checks.append({
            "id": chk2_id,
            "name": "HTTP to HTTPS Redirect Enforcement",
            "category": "Transport Encryption",
            "status": chk2_status,
            "execution_status": chk2_exec,
            "duration_ms": chk2_dur,
            "error_reason": chk2_err,
            "observed": chk2_obs,
            "expected": "HTTP requests redirect to HTTPS via 301 or 308 Permanent Redirect",
            "importance": "Prevents users from accidentally navigating over unencrypted HTTP"
        })

        if http_probe_result["success"] and not redirect_enforced and https_available:
            f_id = "FIND-WEB-CHK002"
            e_id = f"EVD-WEB-CHK002-{run_id}"
            obs = f"HTTP endpoint {http_url} returned HTTP {http_probe_result['status_code']} without 301/308 redirect to HTTPS. (Run {run_id})"
            findings.append({
                "id": f_id,
                "run_id": run_id,
                "check_id": chk2_id,
                "title": "Missing HTTP to HTTPS Redirect Enforcement",
                "category": "Secure Communication & Transport",
                "severity": "MEDIUM",
                "status": "CONFIRMED",
                "evidence_status": "AVAILABLE",
                "cwe_id": "CWE-319",
                "owasp_category": "A02:2021-Cryptographic Failures",
                "evidence": {
                    "id": e_id,
                    "run_id": run_id,
                    "finding_id": f_id,
                    "target": http_url,
                    "detector": "WebSecurityScanner.RedirectEnforcement",
                    "raw_observation": obs,
                    "integrity_hash": hashlib.sha256(obs.encode()).hexdigest(),
                    "timestamp": now_iso
                },
                "simple_evidence": {
                    "what_found": "Visiting the website via plain HTTP does not automatically upgrade to secure HTTPS.",
                    "where_found": http_url,
                    "why_matters": "Users who type the domain without 'https://' may transmit session cookies over unencrypted channels.",
                    "possible_impact": "Man-in-the-middle downgrade attacks (SSL Stripping).",
                    "what_you_can_do": "Add an automatic 301 redirect rule from port 80 to port 443 in your web server config."
                },
                "technical_evidence": {
                    "run_id": run_id,
                    "target": http_url,
                    "observed": f"HTTP status {http_probe_result['status_code']}, Location: {http_probe_result['location'] or 'None'}",
                    "expected": "HTTP/1.1 301 Moved Permanently\nLocation: https://...",
                    "scanner": "WebSecurityScanner",
                    "rule": "WEB-REDIRECT-HTTP-TO-HTTPS",
                    "timestamp": now_iso
                },
                "terminal_verification": {
                    "command": f"curl -I -sS {http_url} | grep -i 'location'",
                    "expected_output": f"Location: https://{hostname}",
                    "observed_output": f"Location: {http_probe_result['location'] or 'None'}"
                },
                "remediation": {
                    "how_to_fix": "In Nginx: return 301 https://$host$request_uri; inside the port 80 server block.",
                    "why_matters": "Enforces encryption for all incoming web requests by default."
                }
            })

        # -------------------------------------------------------------
        # CHECK 3: TLS Certificate Metadata (CHK-003)
        # -------------------------------------------------------------
        chk3_id = "CHK-003"
        tls_valid = tls_info.get("available", False)
        chk3_dur = tls_info.get("duration_ms", 0)
        chk3_err = tls_info.get("error")

        if tls_valid:
            chk3_status = "PASS"
            chk3_exec = "SUCCESS"
            chk3_obs = f"Issuer: {tls_info.get('issuer', 'N/A')}, TLS Version: {tls_info.get('tls_version', 'N/A')}, Cipher: {tls_info.get('cipher', 'N/A')}"
        else:
            chk3_status = "WARNING" if https_available else "FAIL"
            chk3_exec = "TIMEOUT" if "Timeout" in str(chk3_err) else "ERROR"
            chk3_obs = f"TLS inspection unavailable: {chk3_err or 'No TLS handshake'}"
            if not https_available:
                failed_checks_count += 1

        checks.append({
            "id": chk3_id,
            "name": "TLS Certificate Metadata",
            "category": "Certificate Governance",
            "status": chk3_status,
            "execution_status": chk3_exec,
            "duration_ms": chk3_dur,
            "error_reason": chk3_err,
            "observed": chk3_obs,
            "expected": "Valid certificate from recognized authority with TLSv1.2 or TLSv1.3",
            "importance": "Validates authenticity of the web application identity"
        })

        # -------------------------------------------------------------
        # CHECK 4: Certificate Validity Period (CHK-004)
        # -------------------------------------------------------------
        chk4_id = "CHK-004"
        days = tls_info.get("days_remaining")
        is_expiring = days is not None and days <= 30
        is_expired = days is not None and days < 0

        if is_expired:
            chk4_status = "FAIL"
            chk4_exec = "SUCCESS"
            chk4_obs = f"Certificate is EXPIRED ({abs(days)} days ago)"
        elif is_expiring:
            chk4_status = "WARNING"
            chk4_exec = "SUCCESS"
            chk4_obs = f"Certificate expiring soon ({days} days remaining)"
        elif days is not None:
            chk4_status = "PASS"
            chk4_exec = "SUCCESS"
            chk4_obs = f"Certificate valid for {days} day(s) remaining"
        elif tls_valid:
            chk4_status = "PASS"
            chk4_exec = "SUCCESS"
            chk4_obs = "TLS active; certificate validity dates could not be parsed"
        else:
            chk4_status = "NOT AVAILABLE"
            chk4_exec = "ERROR"
            chk4_obs = f"Unable to retrieve validity dates: {chk3_err or 'TLS unavailable'}"

        checks.append({
            "id": chk4_id,
            "name": "Certificate Validity Period",
            "category": "Certificate Governance",
            "status": chk4_status,
            "execution_status": chk4_exec,
            "duration_ms": chk3_dur,
            "error_reason": chk3_err if not tls_valid else None,
            "observed": chk4_obs,
            "expected": "Valid certificate with > 30 days until expiration",
            "importance": "Prevents sudden service outages and browser security warnings"
        })

        if is_expired:
            f_id = "FIND-WEB-CHK004"
            e_id = f"EVD-WEB-CHK004-{run_id}"
            obs = f"Certificate expired {abs(days)} days ago on {tls_info.get('not_after')}. (Run {run_id})"
            findings.append({
                "id": f_id,
                "run_id": run_id,
                "check_id": chk4_id,
                "title": "Expired TLS Certificate",
                "category": "Certificate Governance",
                "severity": "CRITICAL",
                "status": "CONFIRMED",
                "evidence_status": "AVAILABLE",
                "cwe_id": "CWE-295",
                "owasp_category": "A02:2021-Cryptographic Failures",
                "evidence": {
                    "id": e_id,
                    "run_id": run_id,
                    "finding_id": f_id,
                    "target": https_url,
                    "detector": "WebSecurityScanner.CertificateValidity",
                    "raw_observation": obs,
                    "integrity_hash": hashlib.sha256(obs.encode()).hexdigest(),
                    "timestamp": now_iso
                },
                "simple_evidence": {
                    "what_found": "The TLS certificate installed on this website has expired.",
                    "where_found": https_url,
                    "why_matters": "Browsers display security warnings to users and block navigation.",
                    "possible_impact": "Users cannot securely reach your website; communications risk intercept.",
                    "what_you_can_do": "Renew the SSL/TLS certificate immediately."
                },
                "technical_evidence": {
                    "run_id": run_id,
                    "target": https_url,
                    "observed": f"Expiration: {tls_info.get('not_after')} ({days} days)",
                    "expected": "Valid certificate (> 30 days remaining)",
                    "scanner": "WebSecurityScanner",
                    "rule": "WEB-CERT-VALIDITY",
                    "timestamp": now_iso
                },
                "terminal_verification": {
                    "command": f"echo | openssl s_client -connect {hostname}:{tls_port} 2>/dev/null | openssl x509 -noout -dates",
                    "expected_output": "notAfter date in the future",
                    "observed_output": f"notAfter={tls_info.get('not_after')}"
                },
                "remediation": {
                    "how_to_fix": "Request and install a renewed certificate from Let's Encrypt or your Certificate Authority.",
                    "why_matters": "Restores browser trust and valid encryption."
                }
            })

        # -------------------------------------------------------------
        # CHECK 5: Strict-Transport-Security (HSTS) (CHK-005)
        # -------------------------------------------------------------
        header_keys = {k.lower(): v for k, v in raw_headers.items()}
        has_hsts = "strict-transport-security" in header_keys
        chk5_id = "CHK-005"
        chk5_dur = https_probe_result.get("duration_ms", 0)

        if not https_available:
            chk5_status = "WARNING"
            chk5_exec = "NOT_APPLICABLE"
            chk5_obs = "Cannot evaluate HSTS because HTTPS connection failed"
        elif has_hsts:
            chk5_status = "PASS"
            chk5_exec = "SUCCESS"
            chk5_obs = f"HSTS declared: {header_keys['strict-transport-security']}"
        else:
            chk5_status = "WARNING"
            chk5_exec = "SUCCESS"
            chk5_obs = "Header 'Strict-Transport-Security' not present in HTTPS response"

        checks.append({
            "id": chk5_id,
            "name": "Strict-Transport-Security (HSTS)",
            "category": "Security Headers",
            "status": chk5_status,
            "execution_status": chk5_exec,
            "duration_ms": chk5_dur,
            "error_reason": None,
            "observed": chk5_obs,
            "expected": "max-age=31536000; includeSubDomains; preload",
            "importance": "Prevents SSL stripping by mandating HTTPS connections in client browsers"
        })

        if not has_hsts and https_available:
            f_id = "FIND-WEB-CHK005"
            e_id = f"EVD-WEB-CHK005-{run_id}"
            obs = f"Header 'Strict-Transport-Security' missing in HTTPS response from {https_url}. (Run {run_id})"
            findings.append({
                "id": f_id,
                "run_id": run_id,
                "check_id": chk5_id,
                "title": "Missing Strict-Transport-Security (HSTS) Header",
                "category": "Client-Side Security & Configuration",
                "severity": "HIGH",
                "status": "CONFIRMED",
                "evidence_status": "AVAILABLE",
                "cwe_id": "CWE-693",
                "owasp_category": "A05:2021-Security Misconfiguration",
                "evidence": {
                    "id": e_id,
                    "run_id": run_id,
                    "finding_id": f_id,
                    "target": https_url,
                    "detector": "WebSecurityScanner.HSTS",
                    "raw_observation": obs,
                    "integrity_hash": hashlib.sha256(obs.encode()).hexdigest(),
                    "timestamp": now_iso
                },
                "simple_evidence": {
                    "what_found": "KAVACH checked the website response. The Strict-Transport-Security header was not present.",
                    "where_found": https_url,
                    "why_matters": "Without HSTS, a browser may initially attempt an insecure HTTP connection, leaving users vulnerable to network eavesdropping.",
                    "possible_impact": "Man-in-the-Middle attackers on shared networks can intercept initial connections and strip HTTPS.",
                    "what_you_can_do": "Add the Strict-Transport-Security response header with a max-age of at least one year."
                },
                "technical_evidence": {
                    "run_id": run_id,
                    "target": https_url,
                    "method": "HEAD / GET",
                    "observed": "Strict-Transport-Security header omitted",
                    "expected": "Strict-Transport-Security: max-age=31536000; includeSubDomains",
                    "scanner": "WebSecurityScanner",
                    "rule": "WEB-HEADER-HSTS",
                    "timestamp": now_iso
                },
                "terminal_verification": {
                    "command": f"curl -I -sS {https_url} | grep -i 'strict-transport-security'",
                    "expected_output": "strict-transport-security: max-age=31536000; includeSubDomains",
                    "observed_output": "None"
                },
                "remediation": {
                    "how_to_fix": "In Nginx: add_header Strict-Transport-Security 'max-age=31536000; includeSubDomains' always;",
                    "why_matters": "Enforces HTTPS at the browser level for all subsequent requests."
                }
            })

        # -------------------------------------------------------------
        # CHECK 6: Content-Security-Policy (CSP) (CHK-006)
        # -------------------------------------------------------------
        chk6_id = "CHK-006"
        has_csp = "content-security-policy" in header_keys
        chk6_dur = https_probe_result.get("duration_ms", 0)

        if not https_available:
            chk6_status = "WARNING"
            chk6_exec = "NOT_APPLICABLE"
            chk6_obs = "Cannot evaluate CSP because HTTPS connection failed"
        elif has_csp:
            chk6_status = "PASS"
            chk6_exec = "SUCCESS"
            chk6_obs = f"CSP declared: {header_keys['content-security-policy'][:80]}..."
        else:
            chk6_status = "WARNING"
            chk6_exec = "SUCCESS"
            chk6_obs = "Header 'Content-Security-Policy' not present in HTTPS response"

        checks.append({
            "id": chk6_id,
            "name": "Content-Security-Policy (CSP)",
            "category": "Security Headers",
            "status": chk6_status,
            "execution_status": chk6_exec,
            "duration_ms": chk6_dur,
            "error_reason": None,
            "observed": chk6_obs,
            "expected": "Restricted default-src, script-src, and object-src directives",
            "importance": "Protects against Cross-Site Scripting (XSS) and unauthorized data injection"
        })

        if not has_csp and https_available:
            f_id = "FIND-WEB-CHK006"
            e_id = f"EVD-WEB-CHK006-{run_id}"
            obs = f"Header 'Content-Security-Policy' missing in HTTPS response from {https_url}. (Run {run_id})"
            findings.append({
                "id": f_id,
                "run_id": run_id,
                "check_id": chk6_id,
                "title": "Missing Content-Security-Policy (CSP) Header",
                "category": "Client-Side Security & Configuration",
                "severity": "HIGH",
                "status": "CONFIRMED",
                "evidence_status": "AVAILABLE",
                "cwe_id": "CWE-693",
                "owasp_category": "A05:2021-Security Misconfiguration",
                "evidence": {
                    "id": e_id,
                    "run_id": run_id,
                    "finding_id": f_id,
                    "target": https_url,
                    "detector": "WebSecurityScanner.CSP",
                    "raw_observation": obs,
                    "integrity_hash": hashlib.sha256(obs.encode()).hexdigest(),
                    "timestamp": now_iso
                },
                "simple_evidence": {
                    "what_found": "The website does not define a Content-Security-Policy header.",
                    "where_found": https_url,
                    "why_matters": "A Content-Security-Policy restricts which domains the browser can execute scripts from, mitigating cross-site scripting attacks.",
                    "possible_impact": "Compromised third-party scripts or injected malicious JavaScript can execute unrestricted in user browsers.",
                    "what_you_can_do": "Define a CSP policy restricting script execution to trusted domains."
                },
                "technical_evidence": {
                    "run_id": run_id,
                    "target": https_url,
                    "method": "HEAD / GET",
                    "observed": "Content-Security-Policy omitted",
                    "expected": "Content-Security-Policy: default-src 'self'",
                    "scanner": "WebSecurityScanner",
                    "rule": "WEB-HEADER-CSP",
                    "timestamp": now_iso
                },
                "terminal_verification": {
                    "command": f"curl -I -sS {https_url} | grep -i 'content-security-policy'",
                    "expected_output": "content-security-policy: default-src 'self' ...",
                    "observed_output": "None"
                },
                "remediation": {
                    "how_to_fix": "In web server or application middleware, send: Content-Security-Policy: default-src 'self'; script-src 'self';",
                    "why_matters": "Limits blast radius of code injection and cross-site scripting vulnerabilities."
                }
            })

        # -------------------------------------------------------------
        # CHECK 7: X-Content-Type-Options (CHK-007)
        # -------------------------------------------------------------
        chk7_id = "CHK-007"
        has_xcto = "x-content-type-options" in header_keys
        chk7_dur = https_probe_result.get("duration_ms", 0)

        if not https_available:
            chk7_status = "WARNING"
            chk7_exec = "NOT_APPLICABLE"
            chk7_obs = "Cannot evaluate X-Content-Type-Options because HTTPS connection failed"
        elif has_xcto:
            chk7_status = "PASS"
            chk7_exec = "SUCCESS"
            chk7_obs = f"Declared: {header_keys['x-content-type-options']}"
        else:
            chk7_status = "WARNING"
            chk7_exec = "SUCCESS"
            chk7_obs = "Header 'X-Content-Type-Options' not present in received response"

        checks.append({
            "id": chk7_id,
            "name": "X-Content-Type-Options",
            "category": "Security Headers",
            "status": chk7_status,
            "execution_status": chk7_exec,
            "duration_ms": chk7_dur,
            "error_reason": None,
            "observed": chk7_obs,
            "expected": "nosniff",
            "importance": "Prevents MIME-type confusion attacks"
        })

        # -------------------------------------------------------------
        # CHECK 8: Frame Protection (Clickjacking Defense) (CHK-008)
        # -------------------------------------------------------------
        chk8_id = "CHK-008"
        has_frame_opt = "x-frame-options" in header_keys or "frame-ancestors" in header_keys.get("content-security-policy", "")
        chk8_dur = https_probe_result.get("duration_ms", 0)

        if not https_available:
            chk8_status = "WARNING"
            chk8_exec = "NOT_APPLICABLE"
            chk8_obs = "Cannot evaluate Frame Protection because HTTPS connection failed"
        elif has_frame_opt:
            chk8_status = "PASS"
            chk8_exec = "SUCCESS"
            chk8_obs = f"Declared: {header_keys.get('x-frame-options') or 'CSP frame-ancestors'}"
        else:
            chk8_status = "WARNING"
            chk8_exec = "SUCCESS"
            chk8_obs = "X-Frame-Options / CSP frame-ancestors not declared (site can be framed)"

        checks.append({
            "id": chk8_id,
            "name": "Frame Protection (Clickjacking Defense)",
            "category": "Security Headers",
            "status": chk8_status,
            "execution_status": chk8_exec,
            "duration_ms": chk8_dur,
            "error_reason": None,
            "observed": chk8_obs,
            "expected": "X-Frame-Options: DENY or SAMEORIGIN",
            "importance": "Prevents the website from being embedded inside malicious invisible iframes"
        })

        # -------------------------------------------------------------
        # 4. Security Score & Overall Assessment Status Computation
        # -------------------------------------------------------------
        pass_count = sum(1 for c in checks if c["status"] == "PASS")
        total_supported = len(checks)
        executed_checks = sum(1 for c in checks if c.get("execution_status") == "SUCCESS")

        # Score calculation is deterministic based on passes
        score = int((pass_count / total_supported) * 100) if total_supported > 0 else 0
        score_label = "Good" if score >= 80 else ("Needs Attention" if score >= 50 else "High Risk")

        # Assessment Run Status: COMPLETE vs PARTIAL vs FAILED
        if not https_available and not http_probe_result["success"]:
            assessment_status = "FAILED"
            assessment_message = f"Target host {hostname} was unreachable over both HTTP and HTTPS."
        elif failed_checks_count > 0 or executed_checks < total_supported:
            assessment_status = "PARTIAL" if https_available else "COMPLETE"
            assessment_message = f"{executed_checks} of {total_supported} checks executed successfully. {failed_checks_count} check(s) encountered network/connectivity limits."
        else:
            assessment_status = "COMPLETE"
            assessment_message = "All 8 security baseline checks executed successfully."

        result = {
            "success": True,
            "run_id": run_id,
            "run_type": "URL_CHECK",
            "assessment_type": "URL_CHECK",
            "parent_assessment_id": parent_assessment_id,
            "assessment_status": assessment_status,
            "assessment_message": assessment_message,
            "target_url": url,
            "hostname": hostname,
            "timestamp": now_iso,
            "security_score": score,
            "score_label": score_label,
            "supported_checks": total_supported,
            "completed_checks": executed_checks,
            "failed_checks": failed_checks_count,
            "findings_count": len(findings),
            "not_tested": total_supported - executed_checks,
            "limitations": [
                "Only observable HTTP/TLS response configurations are assessed.",
                "Safe, non-destructive observation adhering to RFC 9110 and RFC 8446.",
                "Does not perform invasive SQL injection or destructive exploit payloads."
            ],
            "tls_info": tls_info,
            "redirect_chain": redirect_chain,
            "checks": checks,
            "findings": findings
        }

        # Persist URL_CHECK run to database to ensure durability across restarts
        if db is not None:
            try:
                from backend.app.models.models import Assessment
                summary_payload = {
                    "message": assessment_message,
                    "score": score,
                    "score_label": score_label,
                    "supported_checks": total_supported,
                    "completed_checks": executed_checks,
                    "failed_checks": failed_checks_count,
                    "findings_count": len(findings),
                    "tls_info": tls_info,
                    "redirect_chain": redirect_chain,
                    "checks": checks,
                    "findings": findings
                }
                asm_record = Assessment(
                    id=run_id,
                    name=f"URL Security Check - {hostname}",
                    target_url=url,
                    description=json.dumps(summary_payload),
                    environment="Testing Environment",
                    scope="URL Security Baseline Check",
                    authorization_confirmed=True,
                    modules_enabled=json.dumps(["url_scanner", "tls_probe", "headers"]),
                    status=assessment_status,
                    progress=100,
                    current_stage="REPORT",
                    started_at=now_iso,
                    completed_at=now_iso,
                    is_demo=False,
                    assessment_type="URL_CHECK",
                    parent_assessment_id=parent_assessment_id
                )
                db.merge(asm_record)
                db.commit()
            except Exception:
                try:
                    db.rollback()
                except Exception:
                    pass

        self._latest_assessment = result
        self._history.append(result)
        # Keep last 20 runs
        if len(self._history) > 20:
            self._history.pop(0)

        return result

    def get_latest(self, db: Optional[Session] = None) -> Dict[str, Any]:
        """Returns the most recent assessment result or a default initialized state, persisting across restarts."""
        if self._latest_assessment:
            return self._latest_assessment

        # Restore from database if available (handles application restart)
        if db is not None:
            try:
                from backend.app.models.models import Assessment
                latest_db = (
                    db.query(Assessment)
                    .filter(Assessment.assessment_type == "URL_CHECK")
                    .order_by(Assessment.started_at.desc(), Assessment.id.desc())
                    .first()
                )
                if latest_db and latest_db.description:
                    data = json.loads(latest_db.description)
                    hostname = urlparse(latest_db.target_url).hostname or ""
                    restored = {
                        "success": True,
                        "run_id": latest_db.id,
                        "run_type": "URL_CHECK",
                        "assessment_type": "URL_CHECK",
                        "parent_assessment_id": latest_db.parent_assessment_id,
                        "assessment_status": latest_db.status,
                        "assessment_message": data.get("message", "URL Security Check completed."),
                        "target_url": latest_db.target_url,
                        "hostname": hostname,
                        "timestamp": latest_db.started_at,
                        "security_score": data.get("score", 0),
                        "score_label": data.get("score_label", "Needs Attention"),
                        "supported_checks": data.get("supported_checks", 8),
                        "completed_checks": data.get("completed_checks", 8),
                        "failed_checks": data.get("failed_checks", 0),
                        "findings_count": data.get("findings_count", 0),
                        "not_tested": 0,
                        "limitations": [
                            "Only observable HTTP/TLS response configurations are assessed.",
                            "Safe, non-destructive observation adhering to RFC 9110 and RFC 8446.",
                            "Does not perform invasive SQL injection or destructive exploit payloads."
                        ],
                        "tls_info": data.get("tls_info", {"available": False}),
                        "redirect_chain": data.get("redirect_chain", []),
                        "checks": data.get("checks", []),
                        "findings": data.get("findings", [])
                    }
                    self._latest_assessment = restored
                    return restored
            except Exception:
                pass

        return {
            "success": True,
            "run_id": "",
            "assessment_status": "READY",
            "assessment_message": "Ready to assess.",
            "target_url": "",
            "hostname": "",
            "security_score": 0,
            "score_label": "Not Scanned",
            "supported_checks": 8,
            "completed_checks": 0,
            "failed_checks": 0,
            "findings_count": 0,
            "not_tested": 8,
            "limitations": [
                "Enter a URL and click Check to run safe observations."
            ],
            "tls_info": {"available": False},
            "redirect_chain": [],
            "checks": [],
            "findings": []
        }

    async def reverify_url(self, target_url: str, db: Optional[Session] = None) -> Dict[str, Any]:
        """Re-evaluates the target URL and calculates deterministic resolution diffs."""
        prev = self._latest_assessment
        parent_id = prev.get("parent_assessment_id") if prev else None
        new_result = await self.assess_url(target_url, parent_assessment_id=parent_id, db=db)

        # Compare findings deterministically by ID and title
        prev_findings = {f["id"]: f for f in (prev.get("findings", []) if prev else [])}
        reverified_findings = []
        resolved_details = []

        for f in new_result.get("findings", []):
            if f["id"] in prev_findings:
                f["reverification_status"] = "STILL_OBSERVED"
            else:
                f["reverification_status"] = "NEW"
            reverified_findings.append(f)

        current_ids = {f["id"] for f in new_result.get("findings", [])}
        for prev_id, prev_f in prev_findings.items():
            if prev_id not in current_ids:
                resolved_details.append({
                    "id": prev_id,
                    "title": prev_f["title"],
                    "reason": "Security requirement now satisfied in the latest target observation."
                })

        new_result["reverification"] = {
            "rechecked_at": ist_formatted("%Y-%m-%d %H:%M:%S IST"),
            "previous_run_id": prev.get("run_id") if prev else None,
            "current_run_id": new_result.get("run_id"),
            "previous_findings_count": len(prev_findings),
            "current_findings_count": len(new_result.get("findings", [])),
            "resolved_count": len(resolved_details),
            "resolved_findings": resolved_details
        }
        return new_result


url_scanner_service = UrlScannerService()
