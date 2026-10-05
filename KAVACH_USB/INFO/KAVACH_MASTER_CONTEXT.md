# KAVACH — Master Project Context & Specification
**System Name**: KAVACH (AI-Assisted Security Assessment Platform)  
**Version**: 5.0 Final  
**Context**: KAVACH Enterprise Security Problem Statement Enterprise VAPT  
**Target Application**: World Monitor Situational Intelligence Platform  

---

## 1. Mission Statement & Core Philosophy

KAVACH is an online, evidence-driven security assessment platform engineered to replace opaque, unverified vulnerability scanners with verifiable technical proof. 

Traditional scanners often output vague alerts such as *"SQL Injection Possible"* or *"Broken Access Control Detected"*, forcing security engineers to spend hours validating false positives. KAVACH inverts this model:

$$\text{Facts Discovered} \longrightarrow \text{Evidence Recorded} \longrightarrow \text{Cryptographic Hash Generated} \longrightarrow \text{AI Explains} \longrightarrow \text{User Independently Verifies}$$

### The Absolute Golden Rule
> **KAVACH NEVER SAYS: "Trust us, vulnerability found."**  
> **KAVACH ALWAYS SAYS:**  
> - "Here is what we found."  
> - "Here is where we found it."  
> - "Here is the actual evidence."  
> - "Here is why it matters."  
> - "Here is the technical evidence."  
> - "Here is how you can verify it."  
> - "Here is how you can fix it."

---

## 2. Core Principles & Architecture Rules

1. **Evidence Precedes Everything**: A finding cannot be marked `CONFIRMED` without an accompanying `EvidenceRecord` containing raw response payloads or cryptographic hash verification.
2. **AI Is an Analyst, Not an Oracle**: AI (via local or server-side Ollama) summarizes, explains, and translates evidence into natural language. AI **never** synthesizes vulnerabilities out of thin air.
3. **Deterministic State Machine**: Finding states follow a strict progression:
   $$\text{POTENTIAL} \longrightarrow \text{UNDER ANALYSIS} \longrightarrow \text{VALIDATING} \longrightarrow \text{EVIDENCE AVAILABLE} \longrightarrow \begin{cases} \text{CONFIRMED} \\ \text{UNCONFIRMED} \\ \text{REQUIRES MANUAL REVIEW} \end{cases}$$
4. **Dual Perspective (Simple vs. Technical)**: Every issue can be read by both an executive (simple explanation, business impact, remediation steps) and a penetration tester (exact `curl` command, expected vs. observed diff, raw headers). Both perspectives reference the **same Evidence ID** and **same SHA-256 integrity hash**.
5. **Zero Client Dependencies for Online Users**: Online users access KAVACH via any web browser without needing to install Python, run batch files, or install Ollama models locally. All AI analysis is mediated server-side.

---

## 3. Enterprise Security Audit Standard Alignment

KAVACH is custom-tailored to assess the **World Monitor Application**, covering all 7 mandated assessment categories:
1. **Authentication**: JWT algorithm verification, session token longevity, and brute-force protections.
2. **Authorization & Access Control**: Insecure Direct Object References (IDOR), horizontal privilege escalation across workspaces.
3. **Input Validation & Data Handling**: SQL injection in threat feeds, XSS in telemetry dashboards, schema fuzzing.
4. **API Security**: Missing authentication filters on REST routes, rate limiting bypass, mass assignment.
5. **Client-Side Security**: Missing Content-Security-Policy (CSP), clickjacking vulnerabilities (X-Frame-Options), MIME sniffing.
6. **Secure Communication**: Transport layer security, HSTS enforcement, cookie `Secure` and `SameSite` flags.
7. **Data Storage & Privacy**: Verbose stack traces leaking filesystem paths, database credentials, or tenant tokens.

---

## 4. Key Terminology

- **Target**: An authorized website or REST API service undergoing testing.
- **Assessment**: A scoped assessment job with defined test modules and audit trails.
- **Finding**: A discrete security issue or hypothesis identified during testing.
- **Evidence Record**: An immutable, SHA-256 hashed artifact containing raw network traffic or payload responses proving a finding.
- **Verification Procedure**: A safe, reproducible CLI command (`curl`) allowing independent validation.
- **Re-Verification**: A re-test workflow comparing the original finding against the patched service.
