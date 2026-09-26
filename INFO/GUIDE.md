# KAVACH 6.0 — System User Guide & Technical Documentation

**System**: KAVACH 6.0 Sovereign Security & Cyber Intelligence Platform  
**Target Application**: World Monitor Situational Intelligence Application  
**SIH Problem Statement**: 26163  
**Complete End-User Manual**: See [INFO/USER_MANUAL.md](USER_MANUAL.md) for the 25-chapter operator manual and demonstration index.

---

## 1. System Overview & Dual-Interface Architecture

KAVACH 6.0 operates with two presentation interfaces over a single shared sovereign backend and database (`kavach.db`):
- **Web Application**: High-performance browser-based security workstation built on React 19, TypeScript, and Vite.
- **Desktop Application**: Sovereign native client built with PySide6 / Qt.

Both interfaces query the same assessment engines, evidence repositories, CVSS risk calculators, and cryptographically chained audit trails.

---

## 2. Playable Video Demonstrations

High-definition (1280x720) demonstration recordings are available in `docs/user_manual/demos/` and `frontend/public/demos/`:
1. `getting_started.mp4` — System Boot, Authorization, and 1-Click Onboarding
2. `url_check.mp4` — Instant Standalone HTTP & TLS Security Audit
3. `ai_ready.mp4` — Local Ollama Lifecycle & Sensitive Regex Masking
4. `assess_target.mp4` — 17-Step Autonomous Assessment Pipeline
5. `world_monitor.mp4` — World Monitor Dual-Mode Target Audit (PS 26163)
6. `local_posture.mp4` — Portable USB Zero-Collection Host Scanner
7. `finding.mp4` — Finding Structure, CWE/OWASP Mapping, and Triage
8. `evidence.mp4` — Bitwise SHA-256 Hashes and Terminal Commands
9. `audit_trail.mp4` — Merkle-Style Chained Cryptographic Event Ledger
10. `experience_db.mp4` — Institutional False Positives Repository
11. `history.mp4` — Historical Audit Comparison & Posture Trends
12. `guide.mp4` — Platform Architecture Knowledge Base
13. `user_manual.mp4` — End-User Manual & Interactive Video Player
14. `report_generation.mp4` — Standalone HTML Dossier & JSON Manifest
15. `retest.mp4` — BEFORE vs AFTER Differential State Verification
16. `full_sih_demo.mp4` — Full 17-Step SIH Problem Statement 26163 Demo

---

## 3. Core Functional Modules

### 1. URL Check
- **Purpose**: Target reachability, DNS validation, SSL/TLS certificate inspection, and security header auditing.
- **Output**: Real response headers, TLS handshake details, and identified misconfigurations with SHA-256 evidence.

### 2. World Monitor Assessment
- **Purpose**: Deep security assessment of the World Monitor application across all 7 SIH categories:
  1. Authentication (JWT algorithms, session tokens)
  2. Authorization & Access Control (IDOR, role escalation)
  3. Input Validation & Data Handling (SQLi, XSS fuzzing)
  4. API Security (CORS, rate limiting, REST headers)
  5. Client-Side Security (CSP, MIME sniffing, Clickjacking)
  6. Secure Communication (HTTPS enforcement, HSTS)
  7. Data Storage & Privacy (Stack trace leak, credential exposure)
  8. Dependency Security (AST package auditing)
  9. Source-Code Assessment (Deterministic AST code review)

### 3. Local Posture & Portable Scanners
- **Purpose**: Offline filesystem, process, network socket, and security configuration auditing.
- **Safe Execution**: Uses explicit read-only permissions and hashes all scanned artifacts.

### 4. Findings Catalog
- **5-Point Judge Traceability**:
  1. What code caused the problem?
  2. What happened at runtime?
  3. What evidence proves it?
  4. What is the business impact?
  5. How should it be fixed?

### 5. Evidence System
- **Dual Perspective**:
  - *Simple View*: Executive-friendly summary explaining the observation and impact.
  - *Technical View*: Penetration-tester-grade raw payload capture, HTTP headers, exact `curl` reproduction command, and canonical SHA-256 integrity hash.

### 6. Experience DB
- **Purpose**: Knowledge repository storing verified false-positive suppressions and historical assessment lessons.
- **Enforcement**: Rules matched against incoming findings to prevent recurring false alarms.

### 7. Audit Trail
- **Tamper-Evident Ledger**: Every assessment event, status change, and evidence validation is cryptographically chained (`event_hash = SHA256(prev_hash + payload)`).

---

## 4. SIH PS 26163 Demonstration Quick Start

```bash
# 1. Full-stack development launch (FastAPI + React 19)
"START KAVACH 1.0 .bat"

# 2. Automated clean-state SIH demonstration execution
python scripts/run_sih_demo.py

# 3. Comprehensive automated test suite
TEST_KAVACH.bat
```
