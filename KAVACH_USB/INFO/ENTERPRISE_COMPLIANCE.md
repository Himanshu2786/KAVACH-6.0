# KAVACH — Enterprise VAPT Compliance Matrix

**Standard Reference**: Enterprise Security Assessment of the World Monitor Application  
**Target System**: World Monitor Situational Intelligence & Crisis Response Platform  

---

## 1. Compliance Matrix: 7 Primary Assessment Areas

KAVACH is architected to perform thorough security evaluations across the seven mandated assessment disciplines for the World Monitor application.

| # | Mandated Area | Evaluation Method in KAVACH | Associated CWE / OWASP | Implementation Status |
|---|---|---|---|---|
| **1** | **Authentication** | Validates JWT algorithm negotiation, token longevity, brute force mitigation on `/api/v1/auth/verify`. Checks for weak HMAC keys or `alg: none` exploits. | CWE-306, CWE-347<br>OWASP-A07 | **TESTED / DEMO READY** |
| **2** | **Authorization & Access Control** | Tests for horizontal privilege escalation and IDOR on workspace data (`/api/v1/workspaces/{id}`). Ensures tenant separation is strictly enforced. | CWE-639, CWE-284<br>OWASP-A01 | **REAL & TESTED** |
| **3** | **Input Validation & Data Handling** | Fuzzes threat feed search endpoints (`/api/v1/intel/search`) for SQL injection and cross-site scripting (XSS) input reflection. | CWE-89, CWE-79<br>OWASP-A03 | **REAL & TESTED** |
| **4** | **API Security** | Inspects REST endpoints for missing authentication middleware, mass assignment flaws, and verbose debug tracebacks. | CWE-16, CWE-209<br>OWASP-A05 | **REAL & TESTED** |
| **5** | **Client-Side Security** | Audits response headers for Content-Security-Policy (CSP), X-Frame-Options (Clickjacking), and MIME sniffing mitigations. | CWE-1021, CWE-16<br>OWASP-A05 | **REAL & TESTED** |
| **6** | **Secure Communication** | Validates HTTPS transport, Strict-Transport-Security (HSTS) preload status, and cookie security flags (`Secure`, `HttpOnly`, `SameSite`). | CWE-319, CWE-614<br>OWASP-A02 | **REAL & TESTED** |
| **7** | **Data Storage & Privacy** | Checks for sensitive data exposure in server error responses, unencrypted tokens in logs, and internal path disclosures. | CWE-200, CWE-209<br>OWASP-A04 | **REAL & TESTED** |

---

## 2. Target Environment Status Transparency

To maintain utmost academic and professional honesty, KAVACH labels all target configurations transparently:

- **DEMO / TEST ENVIRONMENT**:
  - The seeded scenario (`https://www.worldmonitor.app`) models the World Monitor crisis tracking platform with authentic simulated REST responses, test tenant tokens, and actual error stack dumps.
- **CONNECTED LIVE TARGET**:
  - When an authorized operator enters a live accessible URL (e.g., `https://example.com` or local World Monitor instance), KAVACH switches to live non-destructive probing via `httpx`.
- **NOT CONFIGURED**:
  - If target endpoints or mock targets are unreachable, KAVACH reports honest status (`INCONCLUSIVE` or `UNREACHABLE`), rather than generating fictitious results.
