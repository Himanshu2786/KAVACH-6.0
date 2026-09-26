# KAVACH — System Limitations & Operating Boundaries

Honesty and technical rigor are fundamental to KAVACH. This document outlines the explicit boundaries, constraints, and known limitations of the platform.

---

## 1. Safety & Non-Destructive Probing Boundaries
- **No Destructive Payloads**: KAVACH intentionally excludes destructive exploit payloads. For example, during SQL injection detection, it tests for query boundary syntax anomalies (`' OR 1=1 --`) and timing delays; it will **never** execute `DROP TABLE`, `UPDATE`, or destructive file writes.
- **No Denial of Service (DoS)**: KAVACH does not perform volumetric traffic exhaustion, stress-testing, or resource starvation attacks against targets.

---

## 2. Network & Authentication Boundaries
- **Internal / Air-Gapped Networks**: KAVACH can only assess targets reachable via TCP/IP from the host server executing the backend. Private enterprise networks protected by VPNs or mutual TLS (mTLS) require proper routing configuration.
- **Authenticated Route Testing**: Deep application states behind complex MFA (Multi-Factor Authentication) or OAuth2 identity providers require valid test session tokens or bearer cookies supplied by the operator.
- **WAF & Cloudflare Filtering**: Web Application Firewalls (e.g., Cloudflare, AWS WAF) may drop probe requests with HTTP 403 Forbidden or CAPTCHA challenges. KAVACH treats these responses honestly as `INCONCLUSIVE` or `MANUAL REVIEW REQUIRED`, rather than assuming a vulnerability exists.

---

## 3. AI & Language Model Boundaries
- **AI Is Not the Vulnerability Detector**: The AI model does not discover vulnerabilities by guessing; it only explains and contextualizes technical evidence captured by probe engines.
- **Offline / Cloud Fallback**: When server-side Ollama is unavailable, KAVACH switches to deterministic rule-based intelligence. While deterministic output is consistent and secure, it does not provide interactive ad-hoc chat capabilities.
- **Model Hallucination Mitigation**: Rigid system prompts restrict the model from asserting facts not present in the supplied evidence. However, users should always rely on the raw technical evidence card and terminal procedure as ground truth.

---

## 4. Re-Verification Limitations
- **Cache Persistence**: Some CDNs or reverse proxies cache HTTP response headers for 60 to 300 seconds. Re-verifying a newly applied header patch may temporarily reflect cached vulnerable responses until edge caches purge.

---

## 5. Windows Portable Assessment (USB Edition) Limitations
- **Standard User Mode vs. Administrator**: KAVACH operates primarily in standard Windows user space. It will never bypass UAC or attempt silent elevation. Processes owned by other users or elevated SYSTEM handles will display "Access Denied" for executable path details unless the user explicitly chooses to run the executable with administrative rights.
- **Zero Persistence & USB Auto-Run**: In accordance with enterprise cybersecurity policies, KAVACH contains zero autorun INF files, does not register startup tasks, and will never auto-execute without explicit user action.
- **File Scanner Boundaries**: The file scanner evaluates only user-selected and approved directory paths. To protect system stability and USB flash drive read cycles, files larger than 5 MB are skipped.
- **Vulnerability Correlation Rigor**: Installed software findings require exact, reliable version numbers extracted from the Windows Registry. When version strings are absent or non-standard, KAVACH classifies the finding as `VERSION UNKNOWN` or `NOT VERIFIED` rather than asserting false positives.
