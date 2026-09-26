"""
KAVACH RAG Document Loader
Loads and standardizes security knowledge from KAVACH Knowledge Engine, database records,
and authoritative cybersecurity baselines (CWE, OWASP, Cloud Security, API Remediation).
"""

import json
import logging
from typing import List, Optional
from sqlalchemy.orm import Session

from backend.app.rag.models import SecurityDocument
from backend.app.models.models import KnowledgeRecord
from backend.app.core.database import SessionLocal

logger = logging.getLogger("kavach.rag.loader")

# Expanded curated security intelligence documents ensuring deep domain coverage
STATIC_SECURITY_KNOWLEDGE: List[SecurityDocument] = [
    SecurityDocument(
        id="DOC-CWE-798-SECRETS",
        title="Hardcoded Credentials & Sensitive Cloud Secret Exposure",
        source="MITRE CWE & KAVACH Cloud Security",
        category="Sensitive Data Exposure",
        cwe_id="CWE-798",
        owasp_category="OWASP-A02:2021 - Cryptographic Failures",
        severity="CRITICAL",
        content=(
            "CWE-798: Use of Hard-coded Credentials. The software contains hard-coded credentials, such as a "
            "password, cryptographic key, AWS Access Key ID, secret key, or private token, which are used for "
            "authentication or inbound/outbound authorization. Hardcoded cloud secrets in source repositories or "
            "distributed configurations allow unauthorized actors to hijack cloud infrastructure, access sensitive "
            "databases, and escalate privileges across cloud tenants without multi-factor authentication."
        ),
        remediation_steps=[
            "Immediately invalidate and rotate all exposed API tokens, AWS Access Keys, and database credentials in the cloud provider IAM console.",
            "Migrate hardcoded secrets to an encrypted secret management vault (e.g. AWS Secrets Manager, HashiCorp Vault, Azure Key Vault).",
            "Enforce automated pre-commit hooks (e.g. git-secrets, detect-secrets, TruffleHog) to prevent future secret commits.",
            "Verify that environment manifests and credentials files (.env, credentials.json, id_rsa) are listed in .gitignore."
        ],
        references=[
            "https://cwe.mitre.org/data/definitions/798.html",
            "https://owasp.org/Top10/A02_2021-Cryptographic_Failures/",
            "https://docs.aws.amazon.com/general/latest/gr/aws-access-keys-best-practices.html"
        ],
        metadata={"domain": "secrets_management", "detection_signature": "AKIA|bearer_token|private_key"}
    ),
    SecurityDocument(
        id="DOC-CWE-89-SQLI",
        title="SQL Injection (SQLi) Prevention and Parameterized Query Architecture",
        source="MITRE CWE & OWASP Foundation",
        category="Injection",
        cwe_id="CWE-89",
        owasp_category="OWASP-A03:2021 - Injection",
        severity="CRITICAL",
        content=(
            "CWE-89: Improper Neutralization of Special Elements in SQL Command (SQL Injection). "
            "The application constructs dynamic database queries by directly concatenating user-controlled "
            "input into SQL strings without parameter binding. An attacker can craft malicious inputs containing "
            "quotes, boolean conditions, or UNION operators to bypass authentication, dump entire database tables, "
            "modify records, or execute administrative stored procedures."
        ),
        remediation_steps=[
            "Use parameterized SQL queries and prepared statements exclusively for all database interactions.",
            "Leverage modern ORM layers (such as SQLAlchemy, Hibernate, or Prisma) with bound query variables.",
            "Apply the principle of least privilege to database service accounts, restricting DROP, ALTER, and cross-schema access.",
            "Implement automated input validation and centralized typing controls before query dispatch."
        ],
        references=[
            "https://cwe.mitre.org/data/definitions/89.html",
            "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"
        ],
        metadata={"domain": "database_security", "attack_vector": "sql_concatenation"}
    ),
    SecurityDocument(
        id="DOC-CWE-639-IDOR",
        title="Insecure Direct Object Reference (IDOR) & Broken Object Level Authorization",
        source="OWASP API Security & MITRE CWE",
        category="Broken Access Control",
        cwe_id="CWE-639",
        owasp_category="OWASP-A01:2021 - Broken Access Control",
        severity="HIGH",
        content=(
            "CWE-639: Authorization Bypass Through User-Controlled Key (IDOR / BOLA). "
            "The system accesses internal resources using user-supplied identifiers (such as record IDs in URLs "
            "or request bodies) without verifying whether the authenticated user has legitimate authorization to access "
            "that specific entity. This permits horizontal privilege escalation where User A retrieves private data belonging to User B."
        ),
        remediation_steps=[
            "Enforce strict server-side tenant ownership validation on every entity query: filter(Record.id == id, Record.owner_id == user.id).",
            "Replace sequential integer identifiers with non-enumerable cryptographic UUIDv4 tokens.",
            "Implement declarative authorization guards or middleware checks before executing business logic.",
            "Perform automated multi-tenant authorization unit and integration testing."
        ],
        references=[
            "https://cwe.mitre.org/data/definitions/639.html",
            "https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/"
        ],
        metadata={"domain": "authorization", "attack_vector": "parameter_tampering"}
    ),
    SecurityDocument(
        id="DOC-CWE-79-XSS",
        title="Cross-Site Scripting (XSS) Mitigation & Context-Aware Output Encoding",
        source="MITRE CWE & OWASP Foundation",
        category="Input Validation",
        cwe_id="CWE-79",
        owasp_category="OWASP-A03:2021 - Injection",
        severity="HIGH",
        content=(
            "CWE-79: Improper Neutralization of Input During Web Page Generation (XSS). "
            "User-supplied input is embedded in web page output without proper contextual encoding or sanitization, "
            "allowing malicious scripts to execute in victim browsers. Reflected, stored, and DOM-based XSS can hijack "
            "session cookies, redirect victims to phishing portals, or perform actions on behalf of the user."
        ),
        remediation_steps=[
            "Apply contextual output encoding (HTML entity encoding, JavaScript variable escaping, URL encoding) prior to DOM insertion.",
            "Deploy a strict Content Security Policy (CSP) header: Content-Security-Policy: default-src 'self'; script-src 'self'.",
            "Mark session and authentication cookies with the HttpOnly flag to prevent script-based cookie extraction.",
            "Utilize modern front-end frameworks (React, Angular, Vue) that escape output variables by default."
        ],
        references=[
            "https://cwe.mitre.org/data/definitions/79.html",
            "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html"
        ],
        metadata={"domain": "web_security", "attack_vector": "script_injection"}
    ),
    SecurityDocument(
        id="DOC-CWE-16-HEADERS",
        title="Defensive HTTP Security Response Headers & Edge Gateway Hardening",
        source="OWASP Secure Headers Project",
        category="Security Misconfiguration",
        cwe_id="CWE-16",
        owasp_category="OWASP-A05:2021 - Security Misconfiguration",
        severity="MEDIUM",
        content=(
            "CWE-16: Configuration Weakness / Missing Defensive Headers. "
            "Web applications lacking essential HTTP security response headers expose users to MIME-type sniffing, "
            "cross-origin data leakage, and iframe framing attacks. Key headers include Content-Security-Policy, "
            "Strict-Transport-Security (HSTS), X-Content-Type-Options, X-Frame-Options, and Referrer-Policy."
        ),
        remediation_steps=[
            "Configure X-Content-Type-Options: nosniff on all static assets and API endpoints to prevent MIME-sniffing exploits.",
            "Add X-Frame-Options: DENY or CSP frame-ancestors 'none' to eliminate UI redressing (Clickjacking).",
            "Enforce Strict-Transport-Security: max-age=31536000; includeSubDomains; preload across all HTTPS listeners.",
            "Set Referrer-Policy: strict-origin-when-cross-origin to protect sensitive query parameters."
        ],
        references=[
            "https://cwe.mitre.org/data/definitions/16.html",
            "https://owasp.org/www-project-secure-headers/"
        ],
        metadata={"domain": "http_headers", "attack_vector": "misconfiguration"}
    ),
    SecurityDocument(
        id="DOC-CWE-306-AUTH",
        title="Authentication Architecture & Multi-Factor Security Enforcement",
        source="MITRE CWE & OWASP ASVS",
        category="Authentication",
        cwe_id="CWE-306",
        owasp_category="OWASP-A07:2021 - Identification and Authentication Failures",
        severity="HIGH",
        content=(
            "CWE-306: Missing Authentication for Critical Function. "
            "The application does not verify user identity before permitting access to critical business functions, "
            "administrative APIs, or sensitive data exports. Lacking authentication boundaries enables unauthenticated "
            "attackers to execute management tasks or exfiltrate core database records."
        ),
        remediation_steps=[
            "Require authenticated session tokens or cryptographically signed JWTs on every API endpoint by default.",
            "Enforce Multi-Factor Authentication (MFA / WebAuthn) for privileged and administrative portals.",
            "Implement centralized authentication middleware that denies unauthenticated requests with HTTP 401.",
            "Prevent broken object level and function level authorization via granular RBAC/ABAC role checks."
        ],
        references=[
            "https://cwe.mitre.org/data/definitions/306.html",
            "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html"
        ],
        metadata={"domain": "authentication", "attack_vector": "missing_auth"}
    ),
    SecurityDocument(
        id="DOC-CWE-918-SSRF",
        title="Server-Side Request Forgery (SSRF) Prevention & Network Segmentation",
        source="OWASP Top 10 & MITRE CWE",
        category="Network & Server Security",
        cwe_id="CWE-918",
        owasp_category="OWASP-A10:2021 - Server-Side Request Forgery (SSRF)",
        severity="HIGH",
        content=(
            "CWE-918: Server-Side Request Forgery (SSRF). "
            "The web server fetches a remote resource without validating the user-supplied destination URL. "
            "An attacker can force the server to issue requests to internal cloud metadata services (e.g. 169.254.169.254), "
            "loopback addresses (127.0.0.1), or private subnet microservices, leaking cloud IAM credentials and internal secrets."
        ),
        remediation_steps=[
            "Strictly whitelist allowed destination hostnames and protocols (enforce https:// only).",
            "Block private IP ranges (RFC 1918, 127.0.0.0/8, 169.254.169.254) at both DNS resolution and network firewall layers.",
            "Disable HTTP redirection following in backend HTTP client libraries.",
            "Deploy IMDSv2 with token hops restricted to 1 on AWS cloud instances."
        ],
        references=[
            "https://cwe.mitre.org/data/definitions/918.html",
            "https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html"
        ],
        metadata={"domain": "ssrf_protection", "attack_vector": "cloud_metadata_abuse"}
    ),
    SecurityDocument(
        id="DOC-CWE-200-APIDOCS",
        title="CWE-200: Public Exposure of API Schema & Interactive Documentation",
        source="MITRE CWE & OWASP API Security",
        category="API Security",
        cwe_id="CWE-200",
        owasp_category="OWASP-A05:2021 - Security Misconfiguration",
        severity="MEDIUM",
        content=(
            "CWE-200: Exposure of Sensitive Information to an Unauthorized Actor. "
            "Public exposure of interactive API schema definitions and documentation (e.g., /openapi.json, /docs, /swagger.json, /redoc) "
            "discloses internal route structures, parameter types, authentication schemes, and API operations to unauthenticated external actors. "
            "How public API schemas aid reconnaissance: While interactive documentation aids legitimate client integration, "
            "unrestricted public access provides external attackers with comprehensive blueprints for automated reconnaissance, "
            "endpoint discovery, and targeted boundary fuzzing without requiring prior reconnaissance. "
            "Important Context: Exposure of API documentation or OpenAPI schemas is an informational exposure weakness and is NOT automatically proof "
            "of unauthorized API access, broken object level authorization, or confirmed backend data breach. "
            "Actual real-world impact depends strictly on whether sensitive internal endpoints, administrative operations, "
            "deprecated parameters, or proprietary operational data structures are disclosed in the published schema."
        ),
        remediation_steps=[
            "Restrict or disable interactive API documentation (/docs, /redoc, /openapi.json) in production environments unless explicitly required for public third-party APIs.",
            "Protect sensitive schema and documentation routes with reverse proxy access controls, API gateway authentication, or IP whitelisting.",
            "Remove internal, administrative, debug, and deprecated endpoints from publicly accessible schema definitions using schema filters or route tags.",
            "Validate that public documentation schemas do not expose internal backend architecture, proprietary data models, or sensitive operational details."
        ],
        references=[
            "https://cwe.mitre.org/data/definitions/200.html",
            "https://owasp.org/API-Security/editions/2023/en/0xa8-security-misconfiguration/",
            "https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html"
        ],
        metadata={
            "domain": "api_security",
            "attack_vector": "schema_reconnaissance",
            "finding_type": "api_documentation_exposure",
            "verification_probe": "curl -k -s -o /dev/null -w \"HTTP %{http_code}\\n\" \"https://<target>/openapi.json\" (Expect HTTP 401/403/404 on production deployments)"
        }
    )
]


class DocumentLoader:
    """Loads security documents from database records and curated intelligence sets."""

    def load_from_db(self, db: Optional[Session] = None) -> List[SecurityDocument]:
        """Fetches KnowledgeRecord entities from database and transforms them into SecurityDocuments."""
        close_session = False
        if db is None:
            db = SessionLocal()
            close_session = True

        try:
            records = db.query(KnowledgeRecord).all()
            docs: List[SecurityDocument] = []

            for r in records:
                # Parse remediation JSON list if stored as string
                remediation_list: List[str] = []
                if r.remediation:
                    try:
                        parsed = json.loads(r.remediation)
                        if isinstance(parsed, list):
                            remediation_list = [str(x) for x in parsed]
                        elif isinstance(parsed, str):
                            remediation_list = [parsed]
                    except Exception:
                        remediation_list = [r.remediation]

                doc = SecurityDocument(
                    id=f"DOC-DB-{r.id}",
                    title=f"{r.id}: {r.title}",
                    content=r.description or f"Security classification and baseline for {r.title}",
                    source=f"KAVACH Knowledge Engine ({r.type})",
                    category=r.category or "General Security",
                    cwe_id=r.id if r.type == "CWE" else None,
                    owasp_category=r.related_owasp or (r.id if r.type == "OWASP" else None),
                    severity="HIGH" if ("injection" in r.title.lower() or "idor" in r.title.lower()) else "MEDIUM",
                    remediation_steps=remediation_list,
                    references=[f"https://cwe.mitre.org/data/definitions/{r.id.split('-')[-1]}.html"] if r.type == "CWE" else [],
                    metadata={"record_type": r.type, "db_id": r.id}
                )
                docs.append(doc)

            return docs
        except Exception as e:
            logger.warning("Could not query KnowledgeRecord table: %s. Relying on static intelligence.", e)
            return []
        finally:
            if close_session:
                db.close()

    def load_all_documents(self, db: Optional[Session] = None) -> List[SecurityDocument]:
        """Combines database knowledge records and curated static security intelligence documents."""
        all_docs: List[SecurityDocument] = list(STATIC_SECURITY_KNOWLEDGE)
        db_docs = self.load_from_db(db)

        # Merge without duplicate IDs
        existing_ids = {d.id for d in all_docs}
        for d in db_docs:
            if d.id not in existing_ids:
                all_docs.append(d)
                existing_ids.add(d.id)

        logger.info("Loaded %d security documents into RAG ingestion pool.", len(all_docs))
        return all_docs


document_loader = DocumentLoader()
