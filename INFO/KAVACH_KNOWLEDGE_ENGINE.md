# KAVACH 6.0 — Knowledge Engine & Standards Mapping

> **KAVACH Version:** 5.0  
> **Documentation Status:** CURRENT (IMPLEMENTED + VERIFIED)  
> **Last Updated:** 2026-09-23  
> **Source of Truth:** Current repository implementation (`seed_data.py`, `correlation_service.py`)  

---

## 1. Overview & Purpose

The **Knowledge Engine** serves as KAVACH's authoritative reference repository. It maps raw scanner observations and technical evidence to official cybersecurity standards:
- **MITRE CWE (Common Weakness Enumeration)**
- **OWASP Top 10 (2021 Categories)**
- **Cloud Security Alliances & CIS Hardening Benchmarks**

Centralizing this mapping prevents divergent classifications across frontend screens and reports.

---

## 2. Core Knowledge Schema

Each record in the `knowledge_items` table contains:
- `id`: Standard identifier (e.g. `CWE-200`, `CWE-798`, `CWE-89`, `CWE-79`).
- `type`: Taxonomy standard (`CWE`, `OWASP`).
- `title`: Formal weakness title.
- `description`: Technical explanation of root cause and attack mechanics.
- `related_owasp`: Corresponding canonical OWASP Top 10 2021 mapping.
- `remediation`: JSON list of engineering remediation steps and hardened configuration examples.
- `category`: Weakness domain (e.g. `Information Exposure`, `Injection`, `Security Misconfiguration`).

---

## 3. Canonical CWE & OWASP Mappings

| Standard ID | Weakness Name | Canonical OWASP | Verified Detection Example | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **`CWE-200`** | Exposure of Sensitive Information to an Unauthorized Actor | **`A05:2021 - Security Misconfiguration`** | Publicly accessible interactive API documentation at `/openapi.json` | `IMPLEMENTED + VERIFIED ON AUTHORIZED WORLD MONITOR` |
| **`CWE-693`** | Protection Mechanism Failure | `A05:2021 - Security Misconfiguration` | Missing baseline HTTP transport defense headers (`HSTS`, `CSP`) | `IMPLEMENTED + TESTED LOCALLY` |
| **`CWE-798`** | Use of Hard-coded Credentials | `A07:2021 - Identification & Auth Failures` | Hardcoded API keys or secrets detected in local source repositories | `IMPLEMENTED + TESTED LOCALLY` |
| **`CWE-89`** | SQL Injection (SQLi) | `A03:2021 - Injection` | Parameter concatenation in SQL database queries | `IMPLEMENTED + TESTED LOCALLY` |
| **`CWE-79`** | Cross-Site Scripting (XSS) | `A03:2021 - Injection` | Unsanitized client-side reflection in HTML/DOM | `IMPLEMENTED + TESTED LOCALLY` |
| **`CWE-942`** | Permissive Cross-Origin Resource Sharing | `A05:2021 - Security Misconfiguration` | Overly permissive CORS wildcard headers with credentials | `IMPLEMENTED + TESTED LOCALLY` |

---

## 4. World Monitor Grounding: Finding WM-API-DOCS-A018

For the verified live target `https://www.worldmonitor.app`:
- **Finding ID**: `WM-API-DOCS-A018`
- **Weakness**: `CWE-200` (*Exposure of Sensitive Information to an Unauthorized Actor*)
- **Canonical OWASP**: `OWASP-A05:2021 - Security Misconfiguration`
- **Technical Context**: Unauthenticated public exposure of the interactive OpenAPI 3.1.0 schema at `/openapi.json`.
- **Finding Severity**: `MEDIUM`
- **Deterministic Priority Score**: `5.92 / 10.0`
- **Scope Boundary**: Reconnaissance and endpoint discovery risk. Not proof of backend execution, database extraction, or privilege escalation.

---

## 5. External Advisory Correlation Rule

> [!IMPORTANT]
> **Strict Isolation Policy**: A shared `CWE` identifier alone does **not** create an external vulnerability correlation.
> 
> For example, an external CISA advisory concerning a Microsoft Windows or Cisco IOS vulnerability categorized under `CWE-200` will **never** be attributed to a web application running on Linux/Node.js simply because both share `CWE-200`. External correlation requires verified technology stack and vendor alignment. When no technology match exists, external advisories display as `NO DIRECT LOCAL MATCH`.
