import os
import json
from backend.app.core.time import ist_isoformat, ist_formatted
from sqlalchemy.orm import Session
from backend.app.models.models import Assessment, Finding, EvidenceRecord, DiscoveryItem, KnowledgeRecord, AuditEvent, User
from backend.app.services.evidence_service import evidence_service
from backend.app.core.security import hash_password, verify_password

def seed_team_users(db: Session):
    """Seed production team accounts if not already present."""
    admin_pw = os.getenv("KAVACH_ADMIN_PASSWORD", "Kavach@Admin2026!")
    team_pw = os.getenv("KAVACH_TEAM_PASSWORD", "Kavach@Team2026!")

    accounts = [
        {
            "id": "ADMIN001",
            "username": "ADMIN001",
            "role": "admin",
            "full_name": "KAVACH System Administrator",
            "password": os.getenv("KAVACH_PASSWORD_ADMIN001", admin_pw)
        },
        {
            "id": "TEAM001",
            "username": "TEAM001",
            "role": "team_member",
            "full_name": "AppSec Specialist 01",
            "password": os.getenv("KAVACH_PASSWORD_TEAM001", team_pw)
        },
        {
            "id": "TEAM002",
            "username": "TEAM002",
            "role": "team_member",
            "full_name": "SecOps Analyst 02",
            "password": os.getenv("KAVACH_PASSWORD_TEAM002", team_pw)
        },
        {
            "id": "TEAM003",
            "username": "TEAM003",
            "role": "team_member",
            "full_name": "Compliance Auditor 03",
            "password": os.getenv("KAVACH_PASSWORD_TEAM003", team_pw)
        },
        {
            "id": "TEAM004",
            "username": "TEAM004",
            "role": "team_member",
            "full_name": "Incident Responder 04",
            "password": os.getenv("KAVACH_PASSWORD_TEAM004", team_pw)
        },
    ]

    for acc in accounts:
        existing = db.query(User).filter(
            (User.id == acc["id"]) | 
            (User.id == f"USR-{acc['id']}") |
            (User.username == acc["username"]) |
            (User.user_id == acc["username"])
        ).first()
        if not existing:
            pw_hash = hash_password(acc["password"])
            u = User(
                id=acc["id"],
                username=acc["username"],
                user_id=acc["username"],
                hashed_password=pw_hash,
                password_hash=pw_hash,
                role=acc["role"],
                full_name=acc["full_name"],
                is_active=True,
                created_at=ist_formatted("%Y-%m-%d %H:%M:%S IST")
            )
            db.add(u)
        else:
            changed = False
            if existing.id != acc["id"]:
                existing.id = acc["id"]
                changed = True
            if existing.username != acc["username"]:
                existing.username = acc["username"]
                changed = True
            if existing.user_id != acc["username"]:
                existing.user_id = acc["username"]
                changed = True
            curr_hash = getattr(existing, "hashed_password", None) or getattr(existing, "password_hash", None)
            if not curr_hash or not verify_password(acc["password"], curr_hash):
                new_hash = hash_password(acc["password"])
                existing.hashed_password = new_hash
                existing.password_hash = new_hash
                changed = True
            if existing.role != acc["role"]:
                existing.role = acc["role"]
                changed = True
            if not getattr(existing, "full_name", None):
                existing.full_name = acc["full_name"]
                changed = True
            if getattr(existing, "is_active", None) is None:
                existing.is_active = True
                changed = True
            if changed:
                db.add(existing)
    db.commit()

def seed_database(db: Session):
    # 0. Provision Team Users
    seed_team_users(db)

    # 1. Bootstrap KAVACH security knowledge base
    knowledge_entries = [
        {
            "id": "CWE-639",
            "type": "CWE",
            "title": "Authorization Bypass Through User-Controlled Key (IDOR)",
            "description": "The system's authorization functionality does not prevent one user from accessing, modifying, or creating data belonging to another user when a user-controlled parameter (such as an ID) is manipulated.",
            "related_owasp": "OWASP-A01:2021 - Broken Access Control",
            "category": "Broken Access Control",
            "remediation": json.dumps([
                "Implement server-side ownership verification on each database entity lookup.",
                "Use non-enumerable cryptographic identifiers (UUIDv4) instead of sequential integers.",
                "Enforce tenant-isolated contextual access filters."
            ])
        },
        {
            "id": "CWE-284",
            "type": "CWE",
            "title": "Improper Access Control",
            "description": "The software does not restrict or incorrectly restricts access to a resource from an unauthorized actor.",
            "related_owasp": "OWASP-A01:2021 - Broken Access Control",
            "category": "Broken Access Control",
            "remediation": json.dumps([
                "Adopt Role-Based (RBAC) or Attribute-Based Access Control (ABAC).",
                "Deny access by default across all routes.",
                "Verify access control checks on every server-side operation."
            ])
        },
        {
            "id": "CWE-89",
            "type": "CWE",
            "title": "Improper Neutralization of Special Elements in SQL Command (SQL Injection)",
            "description": "The software constructs all or part of an SQL command using externally-influenced input from an upstream component, but it does not neutralize or incorrectly neutralizes special elements.",
            "related_owasp": "OWASP-A03:2021 - Injection",
            "category": "Injection",
            "remediation": json.dumps([
                "Use parameterized queries / prepared statements exclusively.",
                "Utilize modern ORMs with bound query variables.",
                "Employ least-privilege database user credentials."
            ])
        },
        {
            "id": "CWE-79",
            "type": "CWE",
            "title": "Improper Neutralization of Input During Web Page Generation (Cross-site Scripting)",
            "description": "The software does not neutralize or incorrectly neutralizes user-controllable input before it is placed in output that is used as a web page that is served to other users.",
            "related_owasp": "OWASP-A03:2021 - Injection",
            "category": "Input Validation",
            "remediation": json.dumps([
                "Contextually encode user output before rendering in DOM.",
                "Deploy a restrictive Content Security Policy (CSP).",
                "Utilize secure UI frameworks with automatic template escaping."
            ])
        },
        {
            "id": "CWE-306",
            "type": "CWE",
            "title": "Missing Authentication for Critical Function",
            "description": "The software does not perform authentication for functionality that requires a provable user identity or that consumes a significant amount of resources.",
            "related_owasp": "OWASP-A07:2021 - Identification and Authentication Failures",
            "category": "Authentication",
            "remediation": json.dumps([
                "Require strong multi-factor authentication for sensitive management APIs.",
                "Verify authentication tokens across all microservices.",
                "Centralize identity verification in API Gateway."
            ])
        },
        {
            "id": "CWE-16",
            "type": "CWE",
            "title": "Configuration Weakness",
            "description": "A configuration weakness is an issue that is introduced during configuration of the application or environment.",
            "related_owasp": "OWASP-A05:2021 - Security Misconfiguration",
            "category": "Security Misconfiguration",
            "remediation": json.dumps([
                "Harden web servers and reverse proxies with strict defensive headers.",
                "Disable debug endpoints and default administrative accounts in production.",
                "Automate infrastructure configuration auditing with baseline compliance."
            ])
        },
        {
            "id": "CWE-1021",
            "type": "CWE",
            "title": "Improper Restriction of Rendered UI Layers or Frames (Clickjacking)",
            "description": "The web application allows itself to be rendered within an iframe, frame, or object tag on an untrusted third-party domain.",
            "related_owasp": "OWASP-A05:2021 - Security Misconfiguration",
            "category": "Security Headers",
            "remediation": json.dumps([
                "Add X-Frame-Options: DENY to all HTTP responses.",
                "Implement Content-Security-Policy with frame-ancestors 'none'."
            ])
        },
        {
            "id": "CWE-200",
            "type": "CWE",
            "title": "Exposure of Sensitive Information to an Unauthorized Actor",
            "description": "The product exposes sensitive information to an actor that is not explicitly authorized to have access to that information.",
            "related_owasp": "OWASP-A05:2021 - Security Misconfiguration",
            "category": "Security Misconfiguration",
            "remediation": json.dumps([
                "Disable interactive API documentation endpoints (/docs, /openapi.json, /swagger) in production environments.",
                "Enforce authentication and role-based access control on sensitive schema endpoints.",
                "Filter API schemas to exclude internal, administrative, or deprecated routes."
            ])
        },
        {
            "id": "OWASP-A01",
            "type": "OWASP",
            "title": "A01:2021 - Broken Access Control",
            "description": "Access control enforces policy such that users cannot act outside of their intended permissions. Failures typically lead to unauthorized information disclosure, modification, or destruction.",
            "related_owasp": "OWASP Top 10:2021 #1",
            "category": "Broken Access Control",
            "remediation": json.dumps([
                "Enforce record ownership checks on every request.",
                "Disable client-side only security checks.",
                "Log all access control failures to SIEM."
            ])
        },
        {
            "id": "OWASP-A03",
            "type": "OWASP",
            "title": "A03:2021 - Injection",
            "description": "User-supplied data is not validated, filtered, or sanitized by the application and is interpreted as code or queries.",
            "related_owasp": "OWASP Top 10:2021 #3",
            "category": "Injection",
            "remediation": json.dumps([
                "Adopt parameterized queries and secure query builders.",
                "Enforce strict positive input validation."
            ])
        },
        {
            "id": "OWASP-A05",
            "type": "OWASP",
            "title": "A05:2021 - Security Misconfiguration",
            "description": "Missing appropriate security hardening across any part of the application stack, or improperly configured permissions on cloud services.",
            "related_owasp": "OWASP Top 10:2021 #5",
            "category": "Security Misconfiguration",
            "remediation": json.dumps([
                "Harden platform configuration and remove unnecessary features.",
                "Send security headers: CSP, HSTS, X-Content-Type-Options."
            ])
        }
    ]

    for k in knowledge_entries:
        existing_k = db.query(KnowledgeRecord).filter(KnowledgeRecord.id == k["id"]).first()
        if not existing_k:
            rec = KnowledgeRecord(
                id=k["id"],
                type=k["type"],
                title=k["title"],
                description=k["description"],
                related_owasp=k["related_owasp"],
                category=k["category"],
                remediation=k["remediation"]
            )
            db.add(rec)
    db.commit()

    # Seed Demo Assessment if not present
    demo_asm_id = "ASM-DEMO-001"
    if db.query(Assessment).filter(Assessment.id == demo_asm_id).first() is not None:
        return

    now_str = ist_isoformat()
    
    demo_assessment = Assessment(
        id=demo_asm_id,
        name="World Monitor Application Security Assessment",
        target_url="https://www.worldmonitor.app",
        description="Comprehensive security assessment of the World Monitor situational intelligence and crisis tracking platform.",
        environment="Demo Environment",
        scope="Complete Application & REST API Surface",
        authorization_confirmed=True,
        modules_enabled=json.dumps(["Authentication", "Authorization", "API Security", "Input Validation", "Security Headers", "Configuration Review"]),
        status="RUNNING",
        progress=65,
        current_stage="VALIDATE",
        started_at=now_str,
        completed_at="",
        is_demo=True,
        assessment_type="DEMO"
    )
    db.add(demo_assessment)
    db.commit()

    # Seed Discovery items for demo assessment
    discovery_service.seed_demo_discovery(db, demo_asm_id)

    # Seed Demo Findings covering all 7 SIH PS 26163 Categories
    demo_findings = [
        {
            "id": "KAV-2026-001",
            "assessment_id": demo_asm_id,
            "title": "Insecure Direct Object Reference (IDOR) in Workspace Retrieval",
            "description": "The endpoint /api/v1/workspaces/{id} accepts arbitrary workspace identifiers and returns private telemetry and API keys without validating whether the requesting user owns the workspace.",
            "category": "Authorization and Access Control",
            "affected_component": "/api/v1/workspaces/{id}",
            "base_severity": "HIGH",
            "priority": "HIGH",
            "priority_score": 8.4,
            "status": "CONFIRMED",
            "evidence_status": "VERIFIED",
            "ai_analysis_status": "COMPLETED",
            "ai_summary": "High likelihood of authorization failure permitting horizontal tenant traversal across workspace boundaries.",
            "ai_hypothesis": "Modifying the numeric ID parameter in the REST path enables unauthorized data retrieval from adjacent tenant workspaces due to missing session-to-tenant tenancy binding.",
            "ai_confidence": 89.0,
            "ai_reasoning_summary": "Correlates with CWE-639. The route handler lacks authorization filter decorators and relies solely on client-supplied path variables.",
            "ai_potential_impact": "Complete disclosure of sensitive workspace telemetry, private API tokens, and confidential incident notes.",
            "cwe_id": "CWE-639",
            "owasp_category": "OWASP-A01",
            "recommended_validation": [
                "Issue GET request with User Alpha authorization header against Workspace ID 9921 (owned by User Bravo)",
                "Inspect response status and confidential payload reflection"
            ],
            "recommended_remediation": [
                "Inject owner_id filter in ORM query lookup",
                "Return HTTP 403 when session principal does not match workspace tenant",
                "Replace integer IDs with UUIDv4"
            ]
        },
        {
            "id": "KAV-2026-002",
            "assessment_id": demo_asm_id,
            "title": "SQL Injection in Threat Intelligence Search Filter",
            "description": "The filter parameter in /api/v1/intel/search accepts unescaped SQL syntax, causing backend database query reflection and error disclosure.",
            "category": "Input Validation and Data Handling",
            "affected_component": "/api/v1/intel/search",
            "base_severity": "CRITICAL",
            "priority": "CRITICAL",
            "priority_score": 9.2,
            "status": "CONFIRMED",
            "evidence_status": "VERIFIED",
            "ai_analysis_status": "COMPLETED",
            "ai_summary": "Critical injection flaw permitting arbitrary SQL query evaluation against application database.",
            "ai_hypothesis": "Direct string interpolation in backend query builders allows attackers to break SQL syntax and extract database metadata or execute arbitrary statements.",
            "ai_confidence": 94.0,
            "ai_reasoning_summary": "Matches CWE-89 signature. User input directly controls SQL token boundary without parameterization.",
            "ai_potential_impact": "Full database read/write access, bypass of authentication tables, potential command execution on underlying database host.",
            "cwe_id": "CWE-89",
            "owasp_category": "OWASP-A03",
            "recommended_validation": [
                "Submit non-destructive quote payload: ' OR 1=1 --",
                "Monitor for SQL syntax error responses and timing delays"
            ],
            "recommended_remediation": [
                "Enforce prepared statements with bind parameters",
                "Adopt SQLAlchemy query builder expressions instead of raw string formatting"
            ]
        },
        {
            "id": "KAV-2026-003",
            "assessment_id": demo_asm_id,
            "title": "Missing Defensive Security Headers on Main Ingress",
            "description": "HTTP response headers on the main web portal lack Content-Security-Policy (CSP), Strict-Transport-Security (HSTS), and X-Content-Type-Options.",
            "category": "Client-Side Security",
            "affected_component": "Nginx Ingress / HTTP Gateway",
            "base_severity": "MEDIUM",
            "priority": "MEDIUM",
            "priority_score": 4.8,
            "status": "CONFIRMED",
            "evidence_status": "VERIFIED",
            "ai_analysis_status": "COMPLETED",
            "ai_summary": "Missing HTTP hardening directives reduce defense-in-depth protection against clickjacking and protocol downgrade.",
            "ai_hypothesis": "The absence of defensive headers allows client browsers to render pages in unauthorized iframes and execute script payloads without CSP mitigation.",
            "ai_confidence": 98.0,
            "ai_reasoning_summary": "Matches CWE-16 and CWE-1021. Baseline HTTP auditing detects missing security headers.",
            "ai_potential_impact": "Susceptibility to UI redressing (clickjacking), MIME-type confusion attacks, and unencrypted HTTP downgrade.",
            "cwe_id": "CWE-16",
            "owasp_category": "OWASP-A05",
            "recommended_validation": [
                "Execute HTTP HEAD request against root URL",
                "Inspect response headers for absence of CSP, HSTS, and X-Frame-Options"
            ],
            "recommended_remediation": [
                "Add Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
                "Add Content-Security-Policy: default-src 'self'",
                "Add X-Frame-Options: DENY and X-Content-Type-Options: nosniff"
            ]
        },
        {
            "id": "KAV-2026-004",
            "assessment_id": demo_asm_id,
            "title": "Permissive JWT Algorithm Negotiation in Token Verification",
            "description": "The token handler accepts JWTs signed with HMAC-SHA256 using public RSA verification keys, or tokens with algorithm specified as 'none'.",
            "category": "Authentication",
            "affected_component": "/api/v1/auth/verify",
            "base_severity": "HIGH",
            "priority": "HIGH",
            "priority_score": 7.8,
            "status": "CONFIRMED",
            "evidence_status": "VERIFIED",
            "ai_analysis_status": "COMPLETED",
            "ai_summary": "Token verification permits algorithm confusion allowing arbitrary authentication bypass.",
            "ai_hypothesis": "If the JWT verification logic does not enforce a strict asymmetric RS256 algorithm whitelist, an attacker can forge administrative tokens.",
            "ai_confidence": 91.0,
            "ai_reasoning_summary": "Matches CWE-306 / CWE-347 pattern. Captured live handshake where alg: none was evaluated without rejection.",
            "ai_potential_impact": "Privilege escalation to administrator by forging arbitrary token claims.",
            "cwe_id": "CWE-306",
            "owasp_category": "OWASP-A07",
            "recommended_validation": [
                "Send test token crafted with alg=none in header to /api/v1/auth/verify",
                "Verify if server returns HTTP 401 Unauthorized"
            ],
            "recommended_remediation": [
                "Explicitly declare algorithms=['RS256'] in PyJWT decode call",
                "Reject any token specifying alg='none' or unexpected HMAC modes"
            ]
        },
        {
            "id": "KAV-2026-005",
            "assessment_id": demo_asm_id,
            "title": "Verbose Database Stack Trace in Error Handling",
            "description": "When an unhandled exception occurs in /api/v1/users/me, the backend returns raw Python traceback with file paths and database connection strings.",
            "category": "Data Storage and Privacy",
            "affected_component": "/api/v1/users/me",
            "base_severity": "LOW",
            "priority": "LOW",
            "priority_score": 3.2,
            "status": "CONFIRMED",
            "evidence_status": "VERIFIED",
            "ai_analysis_status": "COMPLETED",
            "ai_summary": "Information disclosure vulnerability exposing internal server architecture and filesystem paths.",
            "ai_hypothesis": "The FastAPI/Starlette debug mode is enabled or exception handlers lack generic error catchers, leaking internal call stacks to clients.",
            "ai_confidence": 92.0,
            "ai_reasoning_summary": "Matches CWE-209. Technical evidence captured full stack trace upon malformed payload submission.",
            "ai_potential_impact": "Aids attackers in reconnaissance, identifying underlying library versions and internal paths.",
            "cwe_id": "CWE-16",
            "owasp_category": "OWASP-A05",
            "recommended_validation": [
                "Send malformed JSON body to /api/v1/users/me",
                "Inspect response body for Python traceback signatures"
            ],
            "recommended_remediation": [
                "Set DEBUG=False in production environment",
                "Implement a global exception handler returning standardized error schemas"
            ]
        },
        {
            "id": "KAV-2026-006",
            "assessment_id": demo_asm_id,
            "title": "Missing Authorization on Crisis Telemetry Export API",
            "description": "The administrative endpoint /api/v1/telemetry/export serves sensitive real-time crisis data to unauthenticated requests without API key validation.",
            "category": "API Security",
            "affected_component": "/api/v1/telemetry/export",
            "base_severity": "HIGH",
            "priority": "HIGH",
            "priority_score": 8.0,
            "status": "CONFIRMED",
            "evidence_status": "VERIFIED",
            "ai_analysis_status": "COMPLETED",
            "ai_summary": "Unprotected REST API route disclosing internal situation feeds without access token enforcement.",
            "ai_hypothesis": "Route definition lacks authentication dependency injection, allowing unauthenticated scraping.",
            "ai_confidence": 96.0,
            "ai_reasoning_summary": "Direct HTTP GET probe returned 200 OK with confidential coordinates and telemetry without auth headers.",
            "ai_potential_impact": "Mass scraping of proprietary situational intelligence and crisis logistics data.",
            "cwe_id": "CWE-306",
            "owasp_category": "OWASP-A01",
            "recommended_validation": [
                "Send unauthenticated GET request to /api/v1/telemetry/export",
                "Verify HTTP 401 response is enforced"
            ],
            "recommended_remediation": [
                "Inject Depends(get_current_active_user) on telemetry export route",
                "Enforce rate-limiting on bulk export endpoints"
            ]
        },
        {
            "id": "KAV-2026-007",
            "assessment_id": demo_asm_id,
            "title": "Missing Secure and SameSite Attributes on Session Cookies",
            "description": "Session cookies issued by World Monitor authentication handlers do not specify the 'Secure' or 'SameSite' attributes.",
            "category": "Secure Communication",
            "affected_component": "/api/v1/auth/login",
            "base_severity": "MEDIUM",
            "priority": "MEDIUM",
            "priority_score": 5.4,
            "status": "CONFIRMED",
            "evidence_status": "VERIFIED",
            "ai_analysis_status": "COMPLETED",
            "ai_summary": "Session cookie flags omit defensive transport security and CSRF mitigation directives.",
            "ai_hypothesis": "Cookies transmitted without Secure attribute can be intercepted if user navigates over cleartext HTTP.",
            "ai_confidence": 94.0,
            "ai_reasoning_summary": "Set-Cookie header audit confirmed absence of 'Secure' and 'SameSite=Lax' directives.",
            "ai_potential_impact": "Session token leakage via insecure network transport and vulnerability to cross-site request forgery.",
            "cwe_id": "CWE-614",
            "owasp_category": "OWASP-A02",
            "recommended_validation": [
                "Inspect Set-Cookie header directives in login response",
                "Check for Secure, HttpOnly, and SameSite attributes"
            ],
            "recommended_remediation": [
                "Configure Set-Cookie with Secure; HttpOnly; SameSite=Lax",
                "Enforce HTTPS-only domain policies"
            ]
        }
    ]

    for f_data in demo_findings:
        finding = Finding(
            id=f_data["id"],
            assessment_id=f_data["assessment_id"],
            title=f_data["title"],
            description=f_data["description"],
            category=f_data["category"],
            affected_component=f_data["affected_component"],
            base_severity=f_data["base_severity"],
            priority=f_data["priority"],
            priority_score=f_data["priority_score"],
            status=f_data["status"],
            evidence_status=f_data["evidence_status"],
            ai_analysis_status=f_data["ai_analysis_status"],
            ai_summary=f_data["ai_summary"],
            ai_hypothesis=f_data["ai_hypothesis"],
            ai_confidence=f_data["ai_confidence"],
            ai_reasoning_summary=f_data["ai_reasoning_summary"],
            ai_potential_impact=f_data["ai_potential_impact"],
            recommended_validation=json.dumps(f_data["recommended_validation"]),
            recommended_remediation=json.dumps(f_data["recommended_remediation"]),
            cwe_id=f_data["cwe_id"],
            owasp_category=f_data["owasp_category"],
            created_at=now_str,
            updated_at=now_str
        )
        db.add(finding)
    db.commit()

    # Seed Evidence Records for all 7 findings with rich KAVACH USP Fields
    evidence_items = [
        {
            "finding_id": "KAV-2026-001",
            "type": "API Response",
            "desc": "Simulated probe observed HTTP 200 disclosure of tenant_bravo confidential keys under user_alpha token.",
            "raw": "GET /api/v1/workspaces/ws-9921/sensitive HTTP/1.1\nHost: worldmonitor.internal.demo\nAuthorization: Bearer user_alpha_jwt...\n\nHTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"workspace_id\": \"ws-9921\", \"owner\": \"tenant_bravo\", \"api_keys\": [\"wm_live_sec_991823\"], \"status\": \"ACTIVE\"}",
            "result": "CONFIRMED",
            "source": "Automated IDOR Prober",
            "what_found": "KAVACH observed that requesting workspace ws-9921 with User Alpha credentials successfully returned confidential API keys belonging to Tenant Bravo.",
            "why_matters": "An attacker with any valid low-privilege account can enumerate and extract confidential credentials belonging to all other organizations on the platform.",
            "where_found": "Endpoint: /api/v1/workspaces/{id}/sensitive",
            "confidence_level": "HIGH",
            "cmd": "curl -i -s -H 'Authorization: Bearer user_alpha_token' 'https://www.worldmonitor.app/api/v1/workspaces/ws-9921/sensitive'",
            "exp": "HTTP/1.1 403 Forbidden\nContent-Type: application/json\n\n{\"error\": \"access_denied\", \"message\": \"Workspace belongs to different tenant\"}",
            "obs": "HTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"workspace_id\": \"ws-9921\", \"owner\": \"tenant_bravo\", \"api_keys\": [\"wm_live_sec_991823\"], \"status\": \"ACTIVE\"}"
        },
        {
            "finding_id": "KAV-2026-002",
            "type": "API Response",
            "desc": "Backend reflected SQLite syntax error message upon single quote and boolean operator injection.",
            "raw": "POST /api/v1/intel/search HTTP/1.1\nContent-Type: application/json\n\n{\"filter\": \"intel_item' OR 1=1 --\"}\n\nHTTP/1.1 500 Internal Server Error\nContent-Type: text/plain\n\nsqlite3.OperationalError: near 'OR': syntax error. Statement: SELECT * FROM intel_feed WHERE filter LIKE '%intel_item' OR 1=1 --%'",
            "result": "CONFIRMED",
            "source": "SQL Injection Fuzzer",
            "what_found": "KAVACH observed that submitting a single quote and SQL boolean condition to the filter parameter triggered raw database syntax errors.",
            "why_matters": "Attackers can bypass application queries to extract the entire database, alter mission-critical intelligence reports, or corrupt audit records.",
            "where_found": "Endpoint: /api/v1/intel/search (filter parameter)",
            "confidence_level": "HIGH",
            "cmd": "curl -i -s -X POST -H 'Content-Type: application/json' -d '{\"filter\": \"test\\x27 OR 1=1 --\"}' 'https://www.worldmonitor.app/api/v1/intel/search'",
            "exp": "HTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"results\": [], \"count\": 0}",
            "obs": "HTTP/1.1 500 Internal Server Error\nContent-Type: text/plain\n\nsqlite3.OperationalError: near 'OR': syntax error"
        },
        {
            "finding_id": "KAV-2026-003",
            "type": "Security Header Observation",
            "desc": "Header inspection verified complete absence of CSP, HSTS, and X-Frame-Options headers.",
            "raw": "HTTP/1.1 200 OK\nServer: nginx/1.24.0\nDate: Mon, 07 Sep 2026 12:00:00 GMT\nContent-Type: text/html; charset=UTF-8\nConnection: keep-alive\n\n<!DOCTYPE html><html><head><title>World Monitor</title></head>...",
            "result": "CONFIRMED",
            "source": "Header Auditor",
            "what_found": "KAVACH observed that the server response headers do not include Content-Security-Policy, Strict-Transport-Security, or X-Frame-Options.",
            "why_matters": "Without these defensive directives, malicious websites can embed World Monitor in invisible iframes to hijack user clicks (clickjacking) and execute injected scripts.",
            "where_found": "Component: Nginx Ingress / HTTP Gateway",
            "confidence_level": "HIGH",
            "cmd": "curl -i -s -I 'https://www.worldmonitor.app/'",
            "exp": "HTTP/1.1 200 OK\nStrict-Transport-Security: max-age=31536000; includeSubDomains\nContent-Security-Policy: default-src 'self'\nX-Frame-Options: DENY\nX-Content-Type-Options: nosniff",
            "obs": "HTTP/1.1 200 OK\nServer: nginx/1.24.0\nContent-Type: text/html; charset=UTF-8\n(Missing CSP, HSTS, X-Frame-Options)"
        },
        {
            "finding_id": "KAV-2026-004",
            "type": "Authentication Behavior",
            "desc": "JWT verification endpoint accepted token with algorithm specified as 'none'.",
            "raw": "POST /api/v1/auth/verify HTTP/1.1\nAuthorization: Bearer [REDACTED_TOKEN]\n\nHTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"status\": \"authenticated\", \"user\": \"admin\", \"privileges\": [\"ALL\"]}",
            "result": "CONFIRMED",
            "source": "Auth Algorithm Auditor",
            "what_found": "KAVACH observed that the authentication verification endpoint accepted a token with alg: none and granted full administrative privileges.",
            "why_matters": "Any unauthenticated user can construct arbitrary tokens claiming to be administrator and gain unrestricted access without knowing any cryptographic secrets.",
            "where_found": "Endpoint: /api/v1/auth/verify",
            "confidence_level": "HIGH",
            "cmd": "curl -i -s -X POST -H 'Authorization: Bearer [REDACTED_TOKEN]' 'https://www.worldmonitor.app/api/v1/auth/verify'",
            "exp": "HTTP/1.1 401 Unauthorized\nContent-Type: application/json\n\n{\"error\": \"unsupported_algorithm\"}",
            "obs": "HTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"status\": \"authenticated\", \"user\": \"admin\"}"
        },
        {
            "finding_id": "KAV-2026-005",
            "type": "API Response",
            "desc": "Traceback dump confirmed verbose internal exception disclosure on malformed payload.",
            "raw": "PUT /api/v1/users/me HTTP/1.1\nContent-Type: application/json\n\n{\"profile\": {\"age\": \"invalid_string\"}}\n\nHTTP/1.1 500 Internal Server Error\n\nTraceback (most recent call last):\n  File \"/app/handlers/user_controller.py\", line 142, in update_profile\n    target_age = int(payload['profile']['age'])\nValueError: invalid literal for int() with base 10: 'invalid_string'",
            "result": "CONFIRMED",
            "source": "API Schema Fuzzer",
            "what_found": "KAVACH observed that submitting invalid schema parameters returned a full Python stack trace showing local file paths and internal controller methods.",
            "why_matters": "Disclosing server file paths, framework versions, and function names allows attackers to map internal software architecture and plan targeted exploit vectors.",
            "where_found": "Endpoint: /api/v1/users/me",
            "confidence_level": "HIGH",
            "cmd": "curl -i -s -X PUT -H 'Content-Type: application/json' -d '{\"profile\": {\"age\": \"invalid_string\"}}' 'https://www.worldmonitor.app/api/v1/users/me'",
            "exp": "HTTP/1.1 422 Unprocessable Entity\nContent-Type: application/json\n\n{\"error\": \"validation_error\", \"detail\": \"age must be an integer\"}",
            "obs": "HTTP/1.1 500 Internal Server Error\n\nTraceback (most recent call last):\n  File \"/app/handlers/user_controller.py\", line 142"
        },
        {
            "finding_id": "KAV-2026-006",
            "type": "API Response",
            "desc": "Administrative crisis telemetry feed returned live coordinates to unauthenticated client.",
            "raw": "GET /api/v1/telemetry/export HTTP/1.1\nHost: worldmonitor.internal.demo\n\nHTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"telemetry_records\": [{\"crisis_id\": \"CR-882\", \"lat\": 28.6139, \"lon\": 77.2090, \"status\": \"ACTIVE_SURVEILLANCE\"}], \"count\": 1}",
            "result": "CONFIRMED",
            "source": "API Authorization Prober",
            "what_found": "KAVACH observed that the bulk crisis telemetry export route returned confidential surveillance records without any authentication credentials.",
            "why_matters": "Real-time crisis coordinates and situational telemetry are accessible to anyone on the internet, compromising public safety operational security.",
            "where_found": "Endpoint: /api/v1/telemetry/export",
            "confidence_level": "HIGH",
            "cmd": "curl -i -s 'https://www.worldmonitor.app/api/v1/telemetry/export'",
            "exp": "HTTP/1.1 401 Unauthorized\nContent-Type: application/json\n\n{\"error\": \"authentication_required\"}",
            "obs": "HTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"telemetry_records\": [...], \"count\": 1}"
        },
        {
            "finding_id": "KAV-2026-007",
            "type": "Network Header Observation",
            "desc": "Session cookies issued without Secure and SameSite attributes.",
            "raw": "POST /api/v1/auth/login HTTP/1.1\nContent-Type: application/json\n\n{\"username\": \"analyst\", \"password\": \"secret\"}\n\nHTTP/1.1 200 OK\nSet-Cookie: session_id=sess_88319024; Path=/;\nContent-Type: application/json\n\n{\"message\": \"logged in\"}",
            "result": "CONFIRMED",
            "source": "Cookie Flag Auditor",
            "what_found": "KAVACH observed that session cookies set during login omit the Secure and SameSite flags.",
            "why_matters": "Session tokens can be leaked across cleartext HTTP connections during network downgrade and are vulnerable to cross-site request forgery.",
            "where_found": "Endpoint: /api/v1/auth/login (Set-Cookie)",
            "confidence_level": "HIGH",
            "cmd": "curl -i -s -X POST -H 'Content-Type: application/json' -d '{\"username\":\"test\",\"password\":\"test\"}' 'https://www.worldmonitor.app/api/v1/auth/login'",
            "exp": "Set-Cookie: session_id=...; Secure; HttpOnly; SameSite=Lax",
            "obs": "Set-Cookie: session_id=sess_88319024; Path=/; (Missing Secure and SameSite)"
        }
    ]

    for ev in evidence_items:
        evidence_service.create_evidence(
            db=db,
            finding_id=ev["finding_id"],
            evidence_type=ev["type"],
            description=ev["desc"],
            raw_data=ev["raw"],
            validation_result=ev["result"],
            source=ev["source"],
            is_demo=True,
            what_found=ev.get("what_found", ""),
            why_matters=ev.get("why_matters", ""),
            where_found=ev.get("where_found", ""),
            confidence_level=ev.get("confidence_level", "HIGH"),
            verification_command=ev.get("cmd", ""),
            expected_output=ev.get("exp", ""),
            observed_output=ev.get("obs", ""),
            evidence_nature="DEMO DATA"
        )

    print("KAVACH demo scenario ('World Monitor Application') seeded successfully with 7 SIH categories.")
