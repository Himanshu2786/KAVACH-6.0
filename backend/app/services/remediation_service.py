"""
KAVACH 5.0 — Actionable Finding-Specific Remediation & Verification Service
Generates 7-part technically precise remediations:
1. problem
2. root_cause
3. recommended_fix
4. affected_component
5. implementation_guidance
6. security_principle
7. verification_method
"""

import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.models import Finding, EvidenceRecord


class RemediationService:
    """
    Generates finding-specific, actionable remediation guidance and verification methods.
    Prohibits generic 'improve security' text.
    """

    def generate_structured_remediation(self, finding_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates structured 7-field remediation guidance from finding dictionary or model.
        """
        title = finding_data.get("title", "")
        category = finding_data.get("category", "")
        component = finding_data.get("affected_component") or finding_data.get("file") or "System Boundary"
        desc = finding_data.get("description", "")
        detector = finding_data.get("detector") or ""

        cat_lower = category.lower()
        title_lower = title.lower()
        det_upper = detector.upper()

        # 1. HSTS / Cleartext Transport (Domain 6: COMM)
        if "hsts" in title_lower or "cleartext" in title_lower or "SRC_INSECURE_HTTP" in det_upper:
            return {
                "problem": f"HTTP transport layer allows unencrypted cleartext communication on {component}.",
                "root_cause": "Web server / reverse proxy lacks HTTP Strict Transport Security (HSTS) enforcement headers and TLS redirect rules.",
                "recommended_fix": "Enforce HTTPS redirect and configure Strict-Transport-Security header with a minimum 1-year max-age and includeSubDomains directive.",
                "affected_component": component,
                "implementation_guidance": (
                    "# Nginx / Reverse Proxy Directive\n"
                    "server {\n"
                    "    listen 80;\n"
                    "    return 301 https://$host$request_uri;\n"
                    "}\n"
                    "server {\n"
                    "    listen 443 ssl http2;\n"
                    "    add_header Strict-Transport-Security 'max-age=31536000; includeSubDomains; preload' always;\n"
                    "}"
                ),
                "security_principle": "Complete Mediation & Cryptographic Transport Defense (Zero Cleartext Transit)",
                "verification_method": f"curl -k -I \"{component}\" | grep -i Strict-Transport-Security",
                "code_patch": "add_header Strict-Transport-Security 'max-age=31536000; includeSubDomains; preload' always;"
            }

        # 2. Content Security Policy / Client DOM Sinks (Domain 5: CLIENT)
        elif "content-security-policy" in title_lower or "csp" in title_lower or "SRC_DANGEROUS_DOM" in det_upper or (" dom " in f" {title_lower} " or "dom sink" in title_lower or "dom xss" in title_lower):
            return {
                "problem": f"Direct unescaped DOM insertion or missing Content Security Policy (CSP) on {component}.",
                "root_cause": "Client scripts bind user-controlled strings directly into DOM sinks (innerHTML, dangerouslySetInnerHTML) without sanitization.",
                "recommended_fix": "Implement a strict Content-Security-Policy (CSP) restricting script execution and sanitize DOM inputs using DOMPurify.",
                "affected_component": component,
                "implementation_guidance": (
                    "// React / Frontend DOM Sanitization\n"
                    "import DOMPurify from 'dompurify';\n\n"
                    "// Insecure: <div dangerouslySetInnerHTML={{ __html: userInput }} />\n"
                    "// Secure:\n"
                    "const cleanHTML = DOMPurify.sanitize(userInput);\n"
                    "<div dangerouslySetInnerHTML={{ __html: cleanHTML }} />"
                ),
                "security_principle": "Defense in Depth & Context-Aware Output Encoding",
                "verification_method": f"curl -k -I \"{component}\" | grep -i Content-Security-Policy",
                "code_patch": "add_header Content-Security-Policy \"default-src 'self'; script-src 'self'; object-src 'none';\" always;"
            }

        # 3. MIME Sniffing / nosniff (Domain 5: CLIENT)
        elif "x-content-type-options" in title_lower or "sniff" in title_lower:
            return {
                "problem": f"MIME type sniffing defense is absent on {component}.",
                "root_cause": "The web server does not return 'X-Content-Type-Options: nosniff', allowing browsers to execute non-executable files as scripts.",
                "recommended_fix": "Add 'X-Content-Type-Options: nosniff' header to all HTTP response pipelines.",
                "affected_component": component,
                "implementation_guidance": (
                    "# FastAPI / Starlette Middleware Example\n"
                    "@app.middleware('http')\n"
                    "async def add_security_headers(request, call_next):\n"
                    "    response = await call_next(request)\n"
                    "    response.headers['X-Content-Type-Options'] = 'nosniff'\n"
                    "    return response"
                ),
                "security_principle": "Fail-Safe Defaults & Strict Boundary Enforcement",
                "verification_method": f"curl -k -I \"{component}\" | grep -i X-Content-Type-Options",
                "code_patch": "response.headers['X-Content-Type-Options'] = 'nosniff'"
            }

        # 4. Clickjacking / X-Frame-Options (Domain 5: CLIENT)
        elif "clickjacking" in title_lower or "frame" in title_lower:
            return {
                "problem": f"Frame embedding restrictions are missing on {component}.",
                "root_cause": "The HTTP response does not specify X-Frame-Options or CSP frame-ancestors, enabling iframe framing attacks.",
                "recommended_fix": "Configure 'X-Frame-Options: SAMEORIGIN' and CSP 'frame-ancestors 'self'' on all response headers.",
                "affected_component": component,
                "implementation_guidance": (
                    "# Nginx Header Configuration\n"
                    "add_header X-Frame-Options 'SAMEORIGIN' always;\n"
                    "add_header Content-Security-Policy \"frame-ancestors 'self';\" always;"
                ),
                "security_principle": "Defense in Depth & UI Redressing Isolation",
                "verification_method": f"curl -k -I \"{component}\" | grep -i X-Frame-Options",
                "code_patch": "add_header X-Frame-Options 'SAMEORIGIN' always;"
            }

        # 5. Server Banner Disclosure (Domain 7: STORAGE / INFO)
        elif "server banner" in title_lower or "banner disclosure" in title_lower or "SRC_SERVER_HEADER" in det_upper:
            return {
                "problem": f"Detailed server software version banner disclosed in HTTP headers on {component}.",
                "root_cause": "Web server software disclosure directives are enabled by default (e.g. server_tokens on).",
                "recommended_fix": "Disable server version tokens and strip X-Powered-By / Server diagnostic headers.",
                "affected_component": component,
                "implementation_guidance": (
                    "# Nginx Configuration\n"
                    "server_tokens off;\n"
                    "more_clear_headers 'Server' 'X-Powered-By';"
                ),
                "security_principle": "Information Hiding & Attack Surface Minimization",
                "verification_method": f"curl -k -I \"{component}\" | grep -i -E '(Server|X-Powered-By)'",
                "code_patch": "server_tokens off;"
            }

        # 6. Hardcoded Secrets / AWS / DB Passwords / JWT Secret (Domain 1: AUTH / Domain 7: STORAGE)
        elif "jwt" in title_lower or "secret" in title_lower or "aws" in title_lower or "password" in title_lower or "key" in title_lower:
            return {
                "problem": f"Hardcoded credential or cryptographic signing secret embedded in {component}.",
                "root_cause": "Secret tokens were committed into source manifests rather than being loaded from an environment vault at runtime.",
                "recommended_fix": "Revoke exposed credentials immediately, rotate all associated keys, and inject secrets via encrypted environment variables or a key vault.",
                "affected_component": component,
                "implementation_guidance": (
                    "# Python / Environment Configuration\n"
                    "import os\n"
                    "# Insecure: JWT_SECRET = 'hardcoded_secret_key'\n"
                    "# Secure:\n"
                    "JWT_SECRET = os.environ.get('KAVACH_JWT_SECRET')\n"
                    "if not JWT_SECRET:\n"
                    "    raise RuntimeError('Critical security error: KAVACH_JWT_SECRET environment variable is missing!')"
                ),
                "security_principle": "Principle of Least Privilege & Secure Key Management",
                "verification_method": f"git grep -E '(AKIA|JWT_SECRET|PROD_DB_PASSWORD)' \"{component}\"",
                "code_patch": "JWT_SECRET = os.environ['KAVACH_JWT_SECRET']"
            }

        # 7. Unsafe Shell Command Execution (Domain 3: INPUT)
        elif "shell" in title_lower or "command injection" in title_lower or "SRC_SHELL_EXEC" in det_upper:
            return {
                "problem": f"Unsafe shell execution using shell=True or system shell on {component}.",
                "root_cause": "Direct string interpolation into operating system command interpreters allowing shell metacharacter injection.",
                "recommended_fix": "Pass command arguments as an array of discrete arguments with shell=False, and validate arguments against strict regex whitelists.",
                "affected_component": component,
                "implementation_guidance": (
                    "# Python Subprocess Example\n"
                    "import subprocess\n"
                    "# Insecure: subprocess.run(f'ping {user_host}', shell=True)\n"
                    "# Secure:\n"
                    "subprocess.run(['ping', '-c', '4', validated_host], shell=False, check=True)"
                ),
                "security_principle": "Complete Parameter Separation & Non-Executable Data Boundaries",
                "verification_method": f"git grep -E 'shell\\s*=\\s*True|os\\.system' \"{component}\"",
                "code_patch": "subprocess.run(['cmd', arg], shell=False)"
            }

        # 8. SQL Injection (Domain 3: INPUT)
        elif "sql" in title_lower or "query" in title_lower or "SRC_SQL_INJECTION" in det_upper:
            return {
                "problem": f"Dynamic SQL string interpolation detected in query builder on {component}.",
                "root_cause": "Database query strings are assembled via string formatting or f-strings instead of parameterized bind variables.",
                "recommended_fix": "Refactor raw SQL strings to use SQLAlchemy ORM bound queries or parameterized cursor executions.",
                "affected_component": component,
                "implementation_guidance": (
                    "# Parameterized Database Query\n"
                    "# Insecure: cursor.execute(f'SELECT * FROM users WHERE username = \\'{username}\\'')\n"
                    "# Secure:\n"
                    "cursor.execute('SELECT * FROM users WHERE username = :username', {'username': username})"
                ),
                "security_principle": "Parameter Binding & Data/Code Separation",
                "verification_method": f"git grep -E 'cursor\\.execute\\(f|\\.format\\(' \"{component}\"",
                "code_patch": "cursor.execute('SELECT * FROM tbl WHERE id = :id', {'id': val})"
            }

        # 9. CORS Wildcard & Origin Bypass (Domain 4: API)
        elif "cors" in title_lower or "origin" in title_lower or "SRC_CORS_WILDCARD" in det_upper:
            return {
                "problem": f"Overly permissive CORS wildcard origin policy allowing cross-site requests on {component}.",
                "root_cause": "Wildcard origin '*' is configured in CORS middleware alongside credentials=True.",
                "recommended_fix": "Restrict CORS allow_origins to an explicit whitelist of trusted frontend hostnames.",
                "affected_component": component,
                "implementation_guidance": (
                    "# FastAPI CORS Middleware Whitelist\n"
                    "from fastapi.middleware.cors import CORSMiddleware\n\n"
                    "app.add_middleware(\n"
                    "    CORSMiddleware,\n"
                    "    allow_origins=['https://app.kavach.local', 'https://admin.kavach.local'],\n"
                    "    allow_credentials=True,\n"
                    "    allow_methods=['GET', 'POST', 'PUT', 'DELETE'],\n"
                    "    allow_headers=['Authorization', 'Content-Type']\n"
                    ")"
                ),
                "security_principle": "Explicit Trust Boundary & Principle of Least Privilege",
                "verification_method": f"curl -k -I -X OPTIONS \"{component}\" -H \"Origin: https://untrusted-site.com\"",
                "code_patch": "allow_origins=['https://trusted.kavach.local']"
            }

        # 10. Publicly Exposed API Documentation (Domain 4: API)
        elif (
            any(k in title_lower for k in ("openapi", "swagger", "api schema", "api documentation", "interactive api"))
            or (("docs" in title_lower or "documentation" in title_lower) and any(w in (title_lower + " " + cat_lower) for w in ("api", "schema", "endpoint")))
            or "openapi" in component.lower()
            or "swagger" in component.lower()
            or "RULE_OPENAPI_DOCS_EXPOSURE" in det_upper
        ):
            return {
                "problem": desc or f"Interactive API schema and documentation (/openapi.json, Swagger UI, or Redoc) is publicly accessible without restriction on {component}.",
                "root_cause": "OpenAPI/Swagger schema publication is enabled in the production deployment without environment-based gating, access restriction, or internal schema filtering.",
                "recommended_fix": (
                    "Restrict production OpenAPI/Swagger documentation exposure where appropriate, "
                    "require authorization for sensitive API documentation, expose documentation only in intended environments, "
                    "and ensure public API documentation does not disclose sensitive internal endpoints, parameters, schemas, or operational details."
                ),
                "affected_component": component,
                "implementation_guidance": (
                    "# 1. Environment-Gated Documentation (FastAPI / Starlette)\n"
                    "import os\n"
                    "from fastapi import FastAPI\n\n"
                    "# Expose interactive schema documentation only in intended environments (e.g. dev/staging)\n"
                    "is_production = os.environ.get('ENVIRONMENT', '').lower() == 'production'\n\n"
                    "app = FastAPI(\n"
                    "    docs_url=None if is_production else '/docs',\n"
                    "    redoc_url=None if is_production else '/redoc',\n"
                    "    openapi_url=None if is_production else '/openapi.json'\n"
                    ")\n\n"
                    "# 2. Reverse-Proxy Access Control (Nginx / Cloudflare / Envoy)\n"
                    "# Restrict access to schema endpoints to authorized internal IPs or administrative VPNs:\n"
                    "# location ~ ^/(docs|redoc|openapi.json) {\n"
                    "#     allow 10.0.0.0/8;\n"
                    "#     deny all;\n"
                    "# }\n\n"
                    "# 3. Schema Filtering: Ensure public schemas omit internal admin routes and sensitive parameter definitions."
                ),
                "security_principle": "Attack Surface Reduction & Information Exposure Minimization (CWE-200 / OWASP API8:2023)",
                "verification_method": f"curl -s -i \"{component}\" | head -n 1",
                "code_patch": "docs_url=None if is_production else '/docs', openapi_url=None if is_production else '/openapi.json'"
            }

        # 11. Deceptive Double Extension / File Upload (Domain 3: INPUT / Domain 7: STORAGE)
        elif "deceptive" in title_lower or "extension" in title_lower or "SRC_DECEPTIVE_EXTENSION" in det_upper:
            return {
                "problem": f"Deceptive double-extension file masquerading detected on {component}.",
                "root_cause": "File validation relies on superficial extension parsing rather than magic byte inspection and strict extension sanitization.",
                "recommended_fix": "Enforce strict server-side file extension whitelisting, strip secondary extensions, and validate MIME magic bytes via python-magic.",
                "affected_component": component,
                "implementation_guidance": (
                    "# File Validation & Sanitization\n"
                    "import magic\n"
                    "ALLOWED_MIME_TYPES = {'image/png': '.png', 'image/jpeg': '.jpg', 'application/pdf': '.pdf'}\n\n"
                    "def validate_uploaded_file(file_bytes: bytes, filename: str) -> str:\n"
                    "    mime = magic.from_buffer(file_bytes, mime=True)\n"
                    "    if mime not in ALLOWED_MIME_TYPES:\n"
                    "        raise ValueError('Invalid file format rejected by security filter')\n"
                    "    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', filename.split('.')[0])\n"
                    "    return f'{clean_name}{ALLOWED_MIME_TYPES[mime]}'"
                ),
                "security_principle": "Input Validation & Non-Executable Storage Isolation",
                "verification_method": f"Get-ChildItem -Path \"{component}\" -Filter \"*.*.exe\"",
                "code_patch": "validate_uploaded_file(file_bytes, filename)"
            }

        # 12. Dynamic Code Execution eval/exec (Domain 3: INPUT)
        elif "eval" in title_lower or "exec" in title_lower or "SRC_EVAL_EXEC" in det_upper:
            return {
                "problem": f"Dangerous dynamic code execution via eval() or exec() observed in {component}.",
                "root_cause": "Runtime strings are passed directly into dynamic Python interpreter execution sinks.",
                "recommended_fix": "Replace eval() and exec() with safe parsing functions such as ast.literal_eval() or structured JSON deserialization.",
                "affected_component": component,
                "implementation_guidance": (
                    "# Safe AST Evaluation\n"
                    "import ast\n"
                    "# Insecure: data = eval(untrusted_str)\n"
                    "# Secure:\n"
                    "data = ast.literal_eval(untrusted_str)"
                ),
                "security_principle": "Code / Data Strict Separation",
                "verification_method": f"git grep -E '\\b(eval|exec)\\s*\\(' \"{component}\"",
                "code_patch": "ast.literal_eval(untrusted_str)"
            }

        # Default Generic Safe Actionable Template
        return {
            "problem": desc or f"Security control defect observed on {component}.",
            "root_cause": "Missing defensive input validation, weak access control, or insecure default configuration.",
            "recommended_fix": "Enforce strict schema validation on input parameters, reject unauthenticated calls, and sanitize outputs.",
            "affected_component": component,
            "implementation_guidance": (
                "# Pydantic / Schema Validation\n"
                "from pydantic import BaseModel, Field\n\n"
                "class SecureRequestSchema(BaseModel):\n"
                "    parameter: str = Field(..., min_length=1, max_length=128, pattern=r'^[a-zA-Z0-9_.-]+$')"
            ),
            "security_principle": "Fail-Safe Defaults & Input Validation Boundaries",
            "verification_method": f"curl -k -s -o /dev/null -w \"HTTP %{{http_code}}\" \"{component}\"",
            "code_patch": "Apply input validation boundary and status code assertion."
        }

    def get_remediation_plan(self, db: Session, finding_id: str) -> Dict[str, Any]:
        """
        Retrieves a comprehensive 7-point remediation plan for a finding from the database.
        """
        finding = db.query(Finding).filter(Finding.id == finding_id).first()
        if not finding:
            raise ValueError(f"Finding {finding_id} not found")

        records = db.query(EvidenceRecord).filter(EvidenceRecord.finding_id == finding_id).all()
        def _is_retest(e):
            e_id = getattr(e, "id", "") or ""
            return (
                e_id.startswith("EVD-AFT-")
                or getattr(e, "source", "") == "Re-Test Verification Engine"
                or (getattr(e, "evidence_type", "") or "").startswith("Re-Test Verification")
                or "re-test" in (getattr(e, "description", "") or "").lower()
                or "post-fix" in (getattr(e, "description", "") or "").lower()
            )

        baseline_records = [r for r in records if not _is_retest(r)]
        confirmed_baseline = [r for r in baseline_records if r.validation_result == "CONFIRMED"]
        retest_records = [r for r in records if _is_retest(r)]

        if confirmed_baseline:
            evidence_summary = f"Validated by {len(confirmed_baseline)} confirmed baseline technical evidence record(s)."
        elif baseline_records:
            evidence_summary = f"Validated by {len(baseline_records)} baseline technical evidence record(s). Latest status: {baseline_records[-1].validation_result}."
        else:
            evidence_summary = "No technical evidence recorded yet."

        if retest_records or finding.status in ("STILL_OPEN", "VERIFIED_REMEDIATED", "RESOLVED"):
            evidence_summary += f" Verification lifecycle verdict: {finding.status}."

        f_dict = {
            "title": finding.title,
            "category": finding.category,
            "affected_component": finding.affected_component,
            "description": finding.description,
            "detector": finding.cwe_id or ""
        }
        rem = self.generate_structured_remediation(f_dict)

        return {
            "finding_id": finding.id,
            "title": finding.title,
            "category": finding.category,
            "affected_component": finding.affected_component,
            "severity": finding.base_severity,
            "priority": finding.priority,
            "status": finding.status,
            "evidence_status": evidence_summary,
            "problem": rem["problem"],
            "root_cause": rem["root_cause"],
            "recommended_fix": rem["recommended_fix"],
            "implementation_guidance": rem["implementation_guidance"],
            "security_principle": rem["security_principle"],
            "verification_method": rem["verification_method"],
            "code_patch": rem.get("code_patch", ""),
            "quick_fix": rem["recommended_fix"],
            "detailed_fix": rem["implementation_guidance"],
            "code_sample": rem.get("code_patch", ""),
            "cwe_id": finding.cwe_id,
            "owasp_category": finding.owasp_category
        }


remediation_service = RemediationService()

