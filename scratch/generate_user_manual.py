"""
KAVACH 6.0 — Master End-User Manual Generator
Writes INFO/USER_MANUAL.md with 25 exhaustive sections, comprehensive button catalog,
simple + technical dual explanations, and direct links to all 16 demonstration recordings.
"""

import os
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
target_manual = repo_root / "INFO" / "USER_MANUAL.md"

content = """# KAVACH 6.0 — END-USER OPERATOR & EVALUATION MANUAL
> **Document Version:** 5.0.0-PROD-MANUAL  
> **Target Audience:** Smart India Hackathon Judges, Security Auditors, SOC Operators, Developers, and First-Time Users  
> **Scope:** End-to-End Operational Manual with Playable Demonstration Recordings  
> **Classification:** [OFFICIAL OPERATOR GUIDE]  

---

## TABLE OF CONTENTS
1. [What is KAVACH?](#1-what-is-kavach)
2. [What KAVACH is Designed to Do](#2-what-kavach-is-designed-to-do)
3. [Target Security Assessment Workflow](#3-target-security-assessment-workflow)
4. [Getting Started & Launching](#4-getting-started)
5. [Application Interface & Navigation](#5-application-interface)
6. [Dashboard (Central Operations Center)](#6-dashboard)
7. [URL Security Check](#7-url-check)
8. [AI READY (Local AI & Truth Hierarchy)](#8-ai-ready)
9. [ASSESS TARGET (17-Step Autonomous Flow)](#9-assess-target)
10. [WORLD MONITOR (Situational Intelligence & Dual Audit)](#10-world-monitor)
11. [LOCAL POSTURE (Portable Host Scanner)](#11-local-posture)
12. [FINDINGS (Vulnerability Triage & Lifecycle)](#12-finding)
13. [EVIDENCE (Cryptographic Proof & SHA-256 Hashing)](#13-evidence)
14. [AUDIT TRAIL (Chained Tamper-Evident Ledger)](#14-audit-trail)
15. [EXPERIENCE DB (Institutional Knowledge & False Positives)](#15-experience-db)
16. [HISTORY (Assessment Timeline & Comparisons)](#16-history)
17. [GUIDE & Embedded Documentation](#17-guide)
18. [USER MANUAL Viewer](#18-user-manual)
19. [Forensic Reporting (HTML Dossier & JSON Manifest)](#19-reports)
20. [Re-Test & Verification Engine](#20-re-test--verification)
21. [SIH Demonstration Workflow (PS 26163 Quick Start)](#21-sih-demonstration-workflow)
22. [Troubleshooting & Error Recovery](#22-troubleshooting)
23. [Important Limitations & Technical Reality](#23-important-limitations)
24. [Safe and Authorized Usage Guidelines](#24-safe-and-authorized-usage)
25. [Complete Button & Workflow Catalog](#25-complete-button--workflow-catalog)
26. [Demonstration Recording Index](#26-demonstration-recording-index)

---

# 1. WHAT IS KAVACH?

### Simple Explanation
KAVACH 6.0 is an automated cybersecurity auditor in a single software package. It is designed to inspect web applications and software source code for security weaknesses (such as missing encryption headers, open ports, exposed passwords, or authorization flaws). Unlike tools that give confusing warnings without proof, KAVACH captures the exact evidence proving that the vulnerability exists, writes step-by-step instructions showing developers how to fix it, and gives you a copy-pasteable terminal command so you can verify the fix yourself.

### Technical Explanation
KAVACH 6.0 is an air-gapped, offline-first, sovereign cybersecurity assessment and continuous posture validation platform. It implements a deterministic detection engine combining Abstract Syntax Tree (AST) static code analysis, socket-level network inspection, and non-destructive HTTP/TLS runtime probes across 7 standard web security domains. KAVACH operates under a strict **Truth Hierarchy**:
```
RAW OBSERVATION (Bitwise Network / AST Capture)
      ↓
CRYPTOGRAPHIC EVIDENCE (SHA-256 Digest)
      ↓
DETERMINISTIC FINDING (FIRST.org CVSS v3.1 Engine)
      ↓
LOCAL AI EXPLANATION (Ollama LLM with Rule Fallback)
```
- **The Core Axiom:** *AI Hypothesizes. Evidence Confirms. Ollama is NEVER the detector.*

[▶ WATCH DEMO: Getting Started](../../docs/user_manual/demos/getting_started.mp4)

---

# 2. WHAT KAVACH IS DESIGNED TO DO

KAVACH 6.0 is built to address Smart India Hackathon **Problem Statement PS 26163** (*AI-based Cyber Security Assessment Tool / Framework for Web Applications*):

1. **Autonomous 7-Domain Web Auditing:**
   - *Authentication & Session Management* (Cookie security, session hijacking, JWT validation).
   - *Authorization & Access Control* (Broken Object Level Authorization / IDOR).
   - *Input Validation & Data Handling* (SQL injection, XSS, SSRF).
   - *API Security* (REST/GraphQL endpoint exposure, CORS misconfiguration).
   - *Client-Side Security* (CSP policies, clickjacking/X-Frame-Options).
   - *Secure Communication* (TLS 1.2/1.3 enforcement, HSTS preload).
   - *Data Storage & Privacy* (Hardcoded credentials, high-entropy secrets).
2. **Deterministic Risk Scoring:** Calculates mathematical FIRST.org CVSS v3.1 base scores with metric factor breakdowns.
3. **Cryptographic Proof Chain:** Links every observation to a SHA-256 bitwise hash and records every lifecycle event in a Merkle-style chained audit ledger.
4. **Actionable Remediation & Verification:** Delivers structured 7-point remediation code patches and compares BEFORE vs. AFTER states upon re-test.

---

# 3. TARGET SECURITY ASSESSMENT WORKFLOW

Every assessment executed by KAVACH follows a verifiable 17-stage lifecycle:

```
TARGET SELECTION (e.g. https://www.worldmonitor.app)
  ↓
LEGAL CONSENT & DUAL-GATE SCOPE AUTHORIZATION
  ↓
TARGET VALIDATION (Reachability & Handshake Check)
  ↓
START ASSESSMENT (Audit Genesis Event Chained)
  ↓
SOURCE CODE REVIEW (Static AST & Insecure Pattern Parsing)
  ↓
RUNTIME TESTING (Non-Destructive Live HTTP/TLS Probing)
  ↓
DETERMINISTIC FINDING CREATION (Finding ID & CWE/OWASP Mapping)
  ↓
EVIDENCE LINKING (Raw Technical Observation + SHA-256 Checksum)
  ↓
REPRODUCTION STEPS (Operator Command Generation)
  ↓
SAFE PoC GENERATION (Non-Destructive curl Command)
  ↓
CVSS v3.1 CALCULATION (FIRST.org Mathematical Base Score)
  ↓
TECHNICAL IMPACT ANALYSIS (CIA Metric Breakdown)
  ↓
BUSINESS IMPACT ANALYSIS (Structured 5-Point Realistic Threat)
  ↓
REMEDIATION GENERATION (Structured 7-Point Actionable Fix Plan)
  ↓
RE-TESTING & VERIFICATION (BEFORE vs AFTER State Comparison Diff)
  ↓
AUDIT TRAIL LOGGING (Tamper-Evident Chained Event Ledger)
  ↓
REPORT & DOSSIER EXPORT (Self-Contained HTML Dossier & JSON Manifest)
```

[▶ WATCH DEMO: Assess Target Workflow](../../docs/user_manual/demos/assess_target.mp4)

---

# 4. GETTING STARTED

### System Requirements
- **Operating System:** Windows 10/11 (64-bit) or Linux (Ubuntu 22.04+).
- **Python:** Python 3.11.x (included or virtualenv).
- **Node.js:** v18.0.0+ / v20.0.0+ (for Web frontend).
- **Local AI (Optional):** Ollama installed on `http://127.0.0.1:11434` with `phi3` or `llama3`. (System runs 100% deterministically even if Ollama is offline).

### Launching KAVACH 6.0
1. **Full-Stack Development Mode (Backend + Web Browser):**
   - Double-click `START KAVACH 1.0 .bat` or `START KAVACH 2.0 .bat`.
   - Starts FastAPI backend on `http://127.0.0.1:8000` and Vite React on `http://127.0.0.1:5173`.
   - Auto-opens your default web browser.
2. **Native Desktop Application (PySide6 Qt GUI):**
   - Run `python main.py` or execute `dist/KAVACH/KAVACH.exe`.
3. **Automated Verification Suite:**
   - Double-click `TEST_KAVACH.bat` to run all 104 automated tests.

[▶ WATCH DEMO: Getting Started](../../docs/user_manual/demos/getting_started.mp4)

---

# 5. APPLICATION INTERFACE

KAVACH 6.0 features a Cyberpunk Sovereign Dark Glassmorphic UI with real-time Three.js 3D globe visualization.

### Navigation Hierarchy
- **Top Header Bar:** Displays Active Target (`https://www.worldmonitor.app`), System Health Dot (`🟢 AI READY`), Active Assessment ID, and SIH 1-Click Demo Journey Stepper.
- **Left Navigation Sidebar:**
  - *OPERATIONS:* Dashboard, URL Check, Assess Target, World Monitor, Local Posture.
  - *INTELLIGENCE:* Findings, Evidence, Knowledge Correlation, AI Analysis, Risk Prioritization.
  - *DEFENSE & AUDIT:* Remediation Center, Security Reports, Audit Trail, Team Desk, Experience DB, History.
  - *SYSTEM:* System Status, Settings, Guide & User Manual.

---

# 6. DASHBOARD

### Simple Explanation
The Dashboard is your main command center. It gives you an instant birds-eye view of your target application's security posture, active threat severity levels, and quick-launch buttons.

### Technical Explanation
The Dashboard aggregates findings, evidence counts, and audit records from `kavach.db`. It computes a real-time Security Posture Score (0-100) based on weighted CVSS 3.1 severity scores and component criticality.

### Key UI Controls on Dashboard
- **`🚀 START ASSESSMENT` Button:** Opens the New Assessment setup screen.
- **`🌐 CHECK URL` Button:** Opens the instant standalone URL security auditor.
- **`🌍 OPEN WORLD MONITOR` Button:** Opens the World Monitor assessment portal.
- **`💻 AUDIT LOCAL POSTURE` Button:** Opens the zero-collection portable host scanner.

---

# 7. URL CHECK

### Simple Explanation
URL Check is a fast, instant scanner. You type in a website URL, click "Scan URL", and within 2 seconds KAVACH inspects whether the website has basic security protections like HTTPS encryption, clickjacking protection, and secure browser headers.

### Technical Explanation
URL Check executes `backend/app/services/url_scanner_service.py:UrlScannerService.assess_url()`. It initiates an HTTP `GET` and socket-level TLS handshake to probe:
1. HTTP Status code, response headers, and redirect chains.
2. TLS 1.2/1.3 protocol negotiation, cipher suite name, and certificate expiration.
3. Presence and syntax of `Strict-Transport-Security` (HSTS), `Content-Security-Policy` (CSP), `X-Frame-Options`, `X-Content-Type-Options`, and `Referrer-Policy`.
4. Generates an `EvidenceRecord` with a SHA-256 digest of the raw response headers.

[▶ WATCH DEMO: URL Security Check](../../docs/user_manual/demos/url_check.mp4)

---

# 8. AI READY

### Dedicated Deep Dive: Local Ollama AI & Truth Hierarchy

### What AI READY Means in KAVACH
`AI READY` indicates that KAVACH's local AI reasoning service is connected to an on-premise Ollama instance (`http://127.0.0.1:11434`) and is prepared to generate plain-English explanations and remediation guides for verified findings.

### The 4 Lifecycle States
1. `🟢 AI READY`: Ollama daemon is running locally and the selected model (`phi3` or `llama3`) is loaded in memory.
2. `🟡 AI STARTING`: The daemon is initializing or loading model weights.
3. `🟠 MODEL UNAVAILABLE`: Ollama is responding but the requested model is not downloaded.
4. `🔴 AI OFFLINE`: Ollama is unreachable. KAVACH automatically transitions to 100% deterministic rule-based explanations.

### What AI Analyzes & How Prompts are Protected
- **Sensitive Data Masking:** Before any finding context is passed to Ollama, `ollama_service.mask_sensitive_data()` replaces all AWS keys (`AKIA***`), DB passwords (`***[MASKED_PASSWORD]`), and authorization tokens with redacted placeholders.
- **Grounding with Local RAG:** The RAG pipeline (`rag_pipeline.py`) retrieves relevant CWE and OWASP definitions from `rag_vectors.npz` and injects them into the prompt to prevent hallucination.

### What AI NEVER Does in KAVACH
- AI NEVER discovers or invents vulnerabilities.
- AI NEVER generates fake evidence or hashes.
- AI NEVER changes CVSS 3.1 scores.
- AI NEVER transmits data outside `localhost` (127.0.0.1).

[▶ WATCH DEMO: AI Ready & Truth Hierarchy](../../docs/user_manual/demos/ai_ready.mp4)

---

# 9. ASSESS TARGET

### Simple Explanation
"Assess Target" runs a full, autonomous cybersecurity audit against your chosen application. It walks through all 7 security domains, finds vulnerabilities, proves them with evidence, calculates their risk score, and prepares reports.

### Technical Explanation
Executes `world_monitor_assessment_engine.py:WorldMonitorAssessmentEngine.run_assessment()`. Orchestrates AST scanning, live HTTP probing, CVSS calculation, remediation generation, and cryptographic audit chaining.

[▶ WATCH DEMO: Assess Target Pipeline](../../docs/user_manual/demos/assess_target.mp4)

---

# 10. WORLD MONITOR

### Simple Explanation
World Monitor (`https://www.worldmonitor.app`) is the real-world target application audited for Smart India Hackathon PS 26163. KAVACH audits both its live website and its source code repository (`github.com/koala73/worldmonitor`).

### Technical Explanation
World Monitor assessment supports 3 operational modes:
1. `RUNTIME`: Non-destructive live HTTP/TLS probing against `https://www.worldmonitor.app`.
2. `SOURCE`: Static AST analysis, secret pattern detection, and dependency audit of the source repository.
3. `HYBRID`: Correlates static source observations with runtime probe responses to prove vulnerability exploitability.

[▶ WATCH DEMO: World Monitor Assessment](../../docs/user_manual/demos/world_monitor.mp4)

---

# 11. LOCAL POSTURE

### Simple Explanation
Local Posture allows you to plug a USB drive into a workstation and scan local folders for leaked passwords, exposed API keys, suspicious double-extension files, and insecure software without uploading any data to the cloud.

### Technical Explanation
Executes `backend/app/scanners/permissions_manager.py` and `core/scanner/filesystem_scanner.py`. Enforces a strict **Zero-Collection Consent Boundary**—scanning only explicitly user-approved directories.

[▶ WATCH DEMO: Local Posture Scanner](../../docs/user_manual/demos/local_posture.mp4)

---

# 12. FINDING

### Finding Structure & Triage
Every detected vulnerability is assigned a structured `Finding` model:
- **Finding ID:** e.g., `FND-WM-SEC-01`
- **Title:** e.g., *Missing Strict-Transport-Security (HSTS) Header*
- **Severity & Base Score:** `MEDIUM` (CVSS 6.5)
- **CVSS 3.1 Vector:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N`
- **CWE / OWASP:** `CWE-319` / `A02:2021-Cryptographic Failures`
- **Finding Statuses:**
  - `CONFIRMED`: Actively verified by raw evidence.
  - `UNDER_REVIEW`: Assigned to an analyst for triage.
  - `RESOLVED`: Successfully remediated and verified by re-test.
  - `FALSE_POSITIVE`: Verified as an authorized architectural exception.

[▶ WATCH DEMO: Finding Triage & Details](../../docs/user_manual/demos/finding.mp4)

---

# 13. EVIDENCE

### Finding vs. Evidence Distinction
- **Finding:** What KAVACH concluded (e.g., "The server is vulnerable to clickjacking").
- **Evidence:** The raw, unadulterated technical observation that proves it (e.g., verbatim HTTP response headers missing `X-Frame-Options` + SHA-256 hash `8f4b2e...`).

### Integrity Hash Verification
Every evidence record stores an immutable SHA-256 hash computed at the millisecond of capture. Re-running the hash on the raw observation payload guarantees zero post-test tampering.

[▶ WATCH DEMO: Evidence & Cryptographic Proof](../../docs/user_manual/demos/evidence.mp4)

---

# 14. AUDIT TRAIL

### Tamper-Evident Chained Event Ledger
Every action taken in KAVACH is recorded in `AuditEvent`:
```python
event_hash = SHA256(prev_hash + timestamp + actor + action + object + result)
```
- Guarantees complete forensic accountability. If any log entry is modified or deleted, the cryptographic hash chain breaks immediately.

[▶ WATCH DEMO: Chained Audit Trail](../../docs/user_manual/demos/audit_trail.mp4)

---

# 15. EXPERIENCE DB

### Institutional Memory & False Positive Library
Experience DB stores verified architectural exceptions and false positives so that future scans on the same target do not cause alert fatigue.

[▶ WATCH DEMO: Experience Database](../../docs/user_manual/demos/experience_db.mp4)

---

# 16. HISTORY

### Assessment Timeline & Comparisons
The History view tracks all past assessment runs (`ASM-YYYYMMDD-XX`), allowing security managers to track remediation progress and posture score improvements over time.

[▶ WATCH DEMO: Assessment History](../../docs/user_manual/demos/history.mp4)

---

# 17. GUIDE & USER MANUAL

### Built-in Knowledge Systems
The Guide page provides a dual-tab experience:
1. **Architectural Guide:** Explains the underlying design principles, compliance standards, and SIH problem statement requirements.
2. **User Manual & Interactive Demos:** Provides searchable operator instructions with embedded "▶ WATCH DEMO" video players.

[▶ WATCH DEMO: Guide & User Manual](../../docs/user_manual/demos/user_manual.mp4)

---

# 18. REPORTS

### Standalone HTML Dossier & JSON Manifest
1. **Interactive HTML Dossier (`SIH_FORENSIC_DOSSIER_*.html`):** Single self-contained file with embedded dark glassmorphic styling, interactive evidence inspector, and zero cloud dependencies.
2. **Reproducible JSON Package (`SIH_FORENSIC_PACKAGE_*.json`):** 13 mandatory sections with a cryptographic SHA-256 hash manifest for every section.

[▶ WATCH DEMO: Forensic Reporting](../../docs/user_manual/demos/report_generation.mp4)

---

# 19. RE-TEST & VERIFICATION

### BEFORE vs. AFTER State Comparison
When a developer fixes a vulnerability, clicking `⚡ Run Verification Test` re-probes the endpoint and generates a side-by-side comparison:
- **BEFORE:** Shows original flawed HTTP response.
- **AFTER:** Shows patched defensive HTTP response.
- **Status Update:** Automatically updates finding status to `RESOLVED` and logs a `FINDING_RE_VERIFIED` event in the audit trail.

[▶ WATCH DEMO: Re-Test & Verification Diff](../../docs/user_manual/demos/retest.mp4)

---

# 20. SIH DEMONSTRATION WORKFLOW

### Quick Start Guide for SIH PS 26163 Evaluators

1. **Step 1: Launch Platform** -> Run `START KAVACH 1.0 .bat` or `START KAVACH 2.0 .bat`.
2. **Step 2: Verify Status** -> Check top header: `🟢 AI READY` and `SQLite: kavach.db`.
3. **Step 3: 1-Click Demo Journey** -> Click `▶ START DEMO JOURNEY` on the top Demo Journey Bar.
4. **Step 4: Execute SIH Demo** -> Click `RUN SIH DEMO (17 STEPS)`.
5. **Step 5: Review Findings & Evidence** -> Inspect finding `FND-WM-SEC-01`, view raw HTTP evidence, and verify SHA-256 hash.
6. **Step 6: Terminal Verification** -> Click `Technical Terminal` to view the non-destructive `curl` reproduction command.
7. **Step 7: Re-Test Diff** -> Click `⚡ Re-Verify` to view the BEFORE vs. AFTER defensive resolution.
8. **Step 8: Export Forensic Dossier** -> Navigate to `Security Reports` and download the standalone HTML dossier.

[▶ WATCH DEMO: Full SIH 17-Step Demonstration](../../docs/user_manual/demos/full_sih_demo.mp4)

---

# 21. TROUBLESHOOTING & ERROR RECOVERY

| Issue / Error | Root Cause | Solution |
|:---|:---|:---|
| **Backend Unavailable (Port 8000)** | FastAPI server not started | Run `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000` |
| **Frontend Disconnected (Port 5173)** | Vite dev server not running | Run `cd frontend && npm run dev` |
| **AI Status: 🔴 AI OFFLINE** | Ollama daemon not running | Run `ollama serve` or double-click `AI/start_ai.bat`. KAVACH automatically uses rule fallbacks. |
| **Target Unreachable** | Internet disconnected | KAVACH seamlessly runs in local synthetic/demo mode using `demo/training_samples/`. |
| **Video Recording Cannot Play** | Missing media codecs | Ensure modern browser (Chrome/Edge/Firefox) or VLC Player is used for `.mp4` files. |

---

# 22. IMPORTANT LIMITATIONS

1. **Offline Simulated Diffs:** When re-testing without live internet connectivity, KAVACH simulates defensive response diffs to demonstrate verification logic.
2. **Windows CMD Grep:** Verification commands containing `curl | grep` require PowerShell (`Select-String`) or Git Bash on Windows.

---

# 23. SAFE AND AUTHORIZED USAGE

- **Legal Authorization:** KAVACH enforces a mandatory Dual-Gate Scope Authorization dialog before initiating any scan.
- **Zero Destructive Payloads:** Probes use read-only HTTP methods (`GET`, `HEAD`, `OPTIONS`). No fuzzing floods, data-wiping SQL injections, or Denial-of-Service attacks are performed.

---

# 24. COMPLETE BUTTON & WORKFLOW CATALOG

### Comprehensive Catalog of All User-Facing Buttons

#### 1. `▶ START DEMO JOURNEY` / `Next Step`
- **Location:** `DemoJourneyBar.tsx` (Top of Web UI)
- **Purpose:** Guides evaluators through the 17-step SIH demonstration workflow.
- **When to Use:** During live demonstrations or first-time onboarding.
- **How to Use:** Click `▶ START DEMO JOURNEY`, then click `Next Step` to advance.
- **What Happens:** Advances active page view and highlights key assessment milestones.
- **System Action:** Queries backend `/api/system/status` and `/api/assessments/world-monitor/latest`.
- **User Sees:** Step-by-step guidance banner with active progress indicator.
- **Expected Result:** Smooth progression through all 17 assessment stages.
- **Possible States:** Initialized, In-Progress, Completed.
- **Next Action:** Click `Run SIH Demo`.
- **Demo:** `getting_started.mp4`

#### 2. `🚀 SCAN URL`
- **Location:** `UrlSecurityCheckPage.tsx` / `url_check_page.py`
- **Purpose:** Executes instant HTTP/TLS security audit on target URL.
- **When to Use:** When auditing a single web address.
- **How to Use:** Enter URL (e.g., `https://www.worldmonitor.app`) and click `🚀 SCAN URL`.
- **What Happens:** Sends HTTP `GET` and TLS handshake probe.
- **System Action:** Calls `POST /api/url-check/scan`.
- **User Sees:** Real-time progress bar followed by security header checklist.
- **Expected Result:** Displays status code, TLS cipher, and missing header findings.
- **Possible States:** Idle, Scanning (Loading), Success, Error (Unreachable).
- **Next Action:** Review findings and copy verification command.
- **Demo:** `url_check.mp4`

#### 3. `⚡ RUN ASSESSMENT` (World Monitor)
- **Location:** `NewAssessmentPage.tsx` / `world_monitor_page.py`
- **Purpose:** Initiates full 7-domain autonomous assessment on World Monitor.
- **When to Use:** For comprehensive posture evaluation.
- **How to Use:** Select scope domains, check consent confirmation, click `⚡ RUN ASSESSMENT`.
- **System Action:** Calls `POST /api/assessments/world-monitor`.
- **User Sees:** 17-step progress visualizer followed by populated findings table.
- **Expected Result:** Generates findings, evidence, CVSS risk scores, and audit events.
- **Demo:** `world_monitor.mp4`

#### 4. `🔍 VIEW CRYPTOGRAPHIC EVIDENCE`
- **Location:** `FindingsPage.tsx` / `findings_page.py`
- **Purpose:** Opens deep technical evidence inspector for selected finding.
- **When to Use:** When validating whether a detected vulnerability is genuine.
- **How to Use:** Click `🔍 View Cryptographic Evidence` on any finding row.
- **System Action:** Queries `GET /api/evidence` for linked `finding_id`.
- **User Sees:** Verbatim raw HTTP observation, timestamp, and 64-character SHA-256 hash.
- **Expected Result:** Displays immutable evidence proof.
- **Demo:** `evidence.mp4`

#### 5. `⚡ RUN VERIFICATION TEST` (Re-Verify)
- **Location:** `RemediationCenterPage.tsx` / `evidence_page.py`
- **Purpose:** Executes re-test check to compare BEFORE vs. AFTER states.
- **When to Use:** After applying a remediation patch.
- **How to Use:** Click `⚡ Run Verification Test` in Remediation Center.
- **System Action:** Calls `POST /api/evidence/{id}/re-verify`.
- **User Sees:** Side-by-side BEFORE (flawed) vs. AFTER (defensive) diff modal.
- **Expected Result:** Finding status transitions from `CONFIRMED` to `RESOLVED`.
- **Demo:** `retest.mp4`

#### 6. `📄 HTML FORENSIC DOSSIER` / `📦 EXPORT JSON`
- **Location:** `SecurityReportPage.tsx` / `security_report_page.py`
- **Purpose:** Exports reproducible, self-contained forensic reports.
- **When to Use:** When archiving audit results for compliance or regulatory review.
- **How to Use:** Click `📄 HTML Forensic Dossier` or `📦 Export JSON`.
- **System Action:** Calls `GET /api/forensic/export/{id}/html`.
- **User Sees:** Browser download of standalone HTML report or JSON package.
- **Expected Result:** Single-file report opening offline in any browser.
- **Demo:** `report_generation.mp4`

---

# 25. DEMONSTRATION RECORDING INDEX

| Workflow | Manual Section | Video File (docs/ & frontend/public/) | Playable URL / Location |
|:---|:---|:---|:---|
| **Getting Started** | Section 4 | `getting_started.mp4` | `/demos/getting_started.mp4` |
| **URL Security Check** | Section 7 | `url_check.mp4` | `/demos/url_check.mp4` |
| **AI Ready & Truth Hierarchy**| Section 8 | `ai_ready.mp4` | `/demos/ai_ready.mp4` |
| **Assess Target Pipeline** | Section 9 | `assess_target.mp4` | `/demos/assess_target.mp4` |
| **World Monitor Audit** | Section 10 | `world_monitor.mp4` | `/demos/world_monitor.mp4` |
| **Local Posture Scanner** | Section 11 | `local_posture.mp4` | `/demos/local_posture.mp4` |
| **Finding Triage** | Section 12 | `finding.mp4` | `/demos/finding.mp4` |
| **Evidence & SHA-256** | Section 13 | `evidence.mp4` | `/demos/evidence.mp4` |
| **Chained Audit Trail** | Section 14 | `audit_trail.mp4` | `/demos/audit_trail.mp4` |
| **Experience Database** | Section 15 | `experience_db.mp4` | `/demos/experience_db.mp4` |
| **Assessment History** | Section 16 | `history.mp4` | `/demos/history.mp4` |
| **Platform Guide** | Section 17 | `guide.mp4` | `/demos/guide.mp4` |
| **User Manual** | Section 18 | `user_manual.mp4` | `/demos/user_manual.mp4` |
| **Forensic Reporting** | Section 19 | `report_generation.mp4` | `/demos/report_generation.mp4` |
| **Re-Test & Verification** | Section 20 | `retest.mp4` | `/demos/retest.mp4` |
| **Full SIH 17-Step Demo** | Section 21 | `full_sih_demo.mp4` | `/demos/full_sih_demo.mp4` |
"""

with open(target_manual, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully generated {target_manual} ({len(content.splitlines())} lines)!")
