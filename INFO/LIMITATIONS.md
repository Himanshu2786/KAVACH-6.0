# KAVACH 6.0 — System Limitations & Operating Boundaries

> **KAVACH Version:** 5.0  
> **Documentation Status:** CURRENT (IMPLEMENTED + VERIFIED)  
> **Last Updated:** 2026-09-23  
> **Source of Truth:** Current repository implementation  

---

## 1. Operating Environments & Testing Scenarios

Honesty and technical rigor are fundamental to KAVACH. This document outlines the explicit boundaries, constraints, and known limitations across all testing scenarios:

### Authorized Live Target Testing (e.g. World Monitor)
- **Scope**: Testing is strictly restricted to publicly accessible endpoints and authorized paths.
- **Probe Safety**: Non-destructive HTTP GET requests only. Zero fuzzing, zero exploitation, zero denial-of-service payloads.
- **Edge Cache Latency**: CDNs and edge caches (e.g. Cloudflare) may cache responses for 60 to 300 seconds. After applying patches, immediate re-tests may observe cached responses until the edge TTL expires.

### Local Testing Environment
- Evaluates locally running services on `localhost` or `127.0.0.1`.
- Unaffected by CDN caching or edge WAF firewalls.

### Synthetic / Demo Data Partition
- Demo simulations operate with `is_demo: true` and are strictly segregated from live target assessments.
- Demo data must never be used to represent real vulnerability states of production infrastructure.

---

## 2. Specific Subsystem Boundaries

### A. Limitations of Public OpenAPI Exposure Finding (`WM-API-DOCS-A018`)
- **What It Proves**: Proves that the interactive OpenAPI 3.1.0 schema at `/openapi.json` is publicly reachable without authentication.
- **What It Does NOT Prove**:
  - Does **NOT** prove backend database compromise.
  - Does **NOT** prove authentication bypass on underlying data API routes.
  - Does **NOT** prove remote code execution, SQL injection, or server takeover.
  - Does **NOT** prove data exfiltration or integrity loss.
- **Impact Classification**: Classified honestly as an **information exposure and reconnaissance risk** under `CWE-200` / `OWASP-A05:2021 Security Misconfiguration`.

### B. Limitations of Source-Code Analysis & Provenance Guard
- **Source Provenance Requirement**: AST source inspection is deactivated on black-box URL assessments unless a validated local repository path is explicitly configured.
- **Client-Side Bundles**: Client-side JavaScript bundles are not treated as backend source code. KAVACH refuses to assert backend source-code vulnerabilities from minified frontend scripts.

### C. Limitations of AI Conclusions & LLM Grounding
- **AI Does Not Confirm Vulnerabilities**: Local LLMs (`phi3`) have no authority to mark a finding confirmed. Only hard, empirical network responses and SHA-256 evidence can confirm a finding.
- **Negative Bounding**: AI prompts are restricted by negative constraints. If evidence is lacking, the AI is barred from extrapolating worst-case compromises.

### D. Limitations of NVD / CVE Attribution
- **No Speculative CVEs**: KAVACH will never assign a CVE or NVD CVSS score to a finding unless the component and version string have been positively matched against authoritative NVD records.
- For `WM-API-DOCS-A018`, CVE is reported honestly as **`Not Identified`** and NVD CVSS as **`Not Available`**.

### E. Limitations of Automated External Advisory Correlation
- **Shared CWE Isolation**: A shared `CWE` identifier alone does **not** create a valid correlation between an external advisory and a local target.
- External advisories concerning unrelated software (e.g. Microsoft Windows Kernel, Cisco IOS) are flagged as `NO DIRECT LOCAL MATCH` when testing a web application.

### F. Network, WAF & Authentication Boundaries
- **Authenticated Routes**: Deep application states behind multi-factor authentication (MFA) or session cookies require manual credential configuration.
- **WAF Obfuscation**: Web Application Firewalls returning HTTP 403 or CAPTCHA challenges are treated as `MANUAL REVIEW REQUIRED` rather than assumed vulnerabilities.

### G. Offline Fallback Boundaries
- When Ollama is offline, the platform falls back to deterministic rule-based summaries. While completely safe and consistent, dynamic interactive conversational chat is deactivated.
- When ChromaDB is offline, the RAG engine switches to exact keyword matching (`LEXICAL_FALLBACK`).
