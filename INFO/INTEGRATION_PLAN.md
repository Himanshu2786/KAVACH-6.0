# KAVACH — Master Integration Plan & Architectural Preservation Specification
**System Name**: KAVACH (AI-Assisted, Evidence-Driven Security Assessment Platform)  
**Problem Statement**: KAVACH Enterprise (Security Assessment of the World Monitor Application)  
**Status**: Pre-Implementation Integration Blueprint  
**Date**: September 2026  

---

## 1. Executive Mandate: Architectural Preservation

> [!IMPORTANT]
> **Core Architectural Preservation Principle**:
> All new capabilities must connect cleanly into KAVACH's foundational evidence-driven pipeline:
> $$\textbf{ASSESSMENT / DETECTION ENGINE} \longrightarrow \textbf{EVIDENCE ENGINE} \longrightarrow \textbf{RULE ENGINE} \longrightarrow \textbf{AI EXPLANATION} \longrightarrow \textbf{REMEDIATION} \longrightarrow \textbf{AUDIT TRAIL}$$
>
> **Strict Constraints**:
> - DO NOT rewrite the entire project or delete existing modules.
> - DO NOT rename existing files or break existing REST API endpoints.
> - DO NOT duplicate scanners or create separate architectures for new features.
> - DO NOT create fake UI functionality or invent unverified findings.

---

## 2. Audit of Existing System Architecture

### 2.1 Existing Core Modules
| Module | Location | Primary Responsibility |
|---|---|---|
| **Assessment Engine** | `backend/app/services/assessment_service.py` | Manages target scopes, progress lifecycle, and multi-stage execution. |
| **Discovery Service** | `backend/app/services/discovery_service.py` | Catalogs endpoints, components, auth points, and input surfaces for World Monitor. |
| **Detection Engine** | `backend/app/scanners/` | Native Windows collectors: files, processes, software, network, startup, system security. |
| **Permission Manager**| `backend/app/scanners/permissions_manager.py` | Strict consent gating for host inspection categories (`PROCESSES`, `NETWORK`, etc.). |
| **Evidence Engine** | `backend/app/services/evidence_service.py` | Cryptographic SHA-256 evidence hashing, dual view (Simple vs. Technical). |
| **Validation Service**| `backend/app/services/validation_service.py` | CLI reproduction procedures (`curl`), diff calculation, and re-verification. |
| **Risk Engine** | `backend/app/services/risk_service.py` | Multi-factor deterministic scoring (severity, confidence, exposure, component criticalness). |
| **Remediation Engine** | `backend/app/services/remediation_service.py` | Actionable fix playbooks, safe recommendations, and verification checks. |
| **Knowledge Engine** | `backend/app/services/knowledge_service.py` | Offline CWE and OWASP Top 10 knowledge base correlation. |
| **AI Explanation Engine**| `backend/app/services/ollama_service.py`, `ai_analysis_service.py` | Local Ollama grounding with 4-state lifecycle, sensitive data masking, and 7-section structured output. |
| **Audit Engine** | `backend/app/core/audit.py` | Tamper-evident, chronological action logging with module and evidence linkage. |
| **Test Center** | `backend/app/api/routes/test_center.py` | Controlled synthetic tests with expected vs. observed diffs. |
| **Team Desk & Experience DB** | `backend/app/api/routes/team.py`, `experience.py` | Finding triage, team notes, false positive libraries, and lessons learned. |

### 2.2 Existing REST API Surface
All routes are mounted under prefix `/api`:
- **System**: `GET /api/health`, `GET /api/system/status`, `GET /api/system/audit`
- **Assessments**: `POST /api/assessments`, `GET /api/assessments`, `GET /api/assessments/{id}`
- **Discovery**: `GET /api/discovery`, `POST /api/discovery/seed`
- **Findings**: `GET /api/findings`, `GET /api/findings/{id}`, `POST /api/findings/{id}/analyze`
- **Evidence**: `GET /api/evidence/{finding_id}`, `GET /api/evidence/{finding_id}/terminal`, `POST /api/evidence/{finding_id}/re-verify`
- **Portable Scanners**: `GET /api/portable/permissions`, `POST /api/portable/permissions`, `POST /api/portable/scan`, `GET /api/portable/results`
- **AI Explanation**: `GET /api/ai/status`, `POST /api/ai/start`, `POST /api/ai/explain-finding`, `POST /api/ai/explain-risk`, `POST /api/ai/remediation-guide`, `POST /api/ai/threat-alert`
- **Team Desk**: `GET /api/team/members`, `GET /api/team/assignments`, `POST /api/team/assign`, `POST /api/team/notes`
- **Experience DB**: `GET /api/experience/summary`, `GET /api/experience/re-verifications`, `GET /api/experience/false-positives`, `POST /api/experience/mark-false-positive`
- **Test Center**: `GET /api/test-center/suites`, `POST /api/test-center/run`
- **Reports**: `GET /api/reports/executive/{id}`, `GET /api/reports/html/{id}`

### 2.3 Existing Scanners (`backend/app/scanners/`)
- `file_scanner.py`: Inspects files for credentials, dangerous extensions, and permissions.
- `process_scanner.py`: Inspects active Windows processes, command lines, parent PIDs, and memory usage.
- `network_scanner.py`: Inspects open listening sockets, established TCP connections, and network adapters.
- `software_scanner.py`: Enumerate installed software and version metadata.
- `startup_scanner.py`: Detects startup keys, registry run keys, and scheduled tasks.
- `system_security_scanner.py`: Checks Windows Defender, Firewall, and UAC status.

### 2.4 Database Structure (`backend/app/models/models.py`)
- **`assessments`**: Core assessment session entity.
- **`discovery_items`**: Attack surface discovery items.
- **`findings`**: Identified security issues with severity, priority score, CWE/OWASP mapping, and triage status.
- **`evidence_records`**: Cryptographic evidence records with SHA-256 hash, raw data, simple/technical views, and terminal commands.
- **`re_verifications`**: Before/after verification diff records.
- **`knowledge_records`**: Offline CWE and OWASP definitions.
- **`audit_events`**: Immutable audit logs with action, module, status, timestamp, and metadata.
- **`system_settings`**: Key-value system configurations.

### 2.5 UI Structure (`frontend/src/`)
- **Layout**: `Navbar.tsx` (Top bar with brand, active target, AI status), `WorkspaceSubnav.tsx` (Horizontal module tabs), `DemoJourneyBar.tsx`.
- **Pages**: `HomePage`, `CommandCenterPage`, `NewAssessmentPage`, `DiscoveryPage`, `AssessmentProgressPage`, `FindingsPage`, `FindingDetailPage`, `EvidenceValidationPage`, `AiAnalysisPage`, `RiskPrioritizationPage`, `RemediationCenterPage`, `SecurityReportPage`, `AssessmentHistoryPage`, `SystemStatusPage`, `PortableAssessmentPage`, `TeamDeskPage`, `ExperienceDbPage`, `TestCenterPage`, `AuditTrailPage`, `GuidePage`, `SettingsPage`.

---

## 3. New Feature Integration Points & Architecture Mapping

```
                                      KAVACH CORE ARCHITECTURE
                                                  │
                ┌─────────────────────────────────┼─────────────────────────────────┐
                ▼                                 ▼                                 ▼
        ASSESSMENT ENGINE                  DETECTION ENGINE                  EVIDENCE ENGINE
        • World Monitor (Enterprise VAPT)         • File Scanner                    • SHA-256 Hashing
        • URL Assessment [FEAT 4]          • Process Scanner                 • Dual Perspective:
          └─ Real Vulnerabilities           • Network Scanner                   - Simple View
             [FEAT 5]                        ├─ Malware / Trojans [FEAT 1]      - Technical View
                                             ├─ Worm Behaviors   [FEAT 2]    • CLI Reproduction
                                             └─ Port 8080 Check  [FEAT 3]
                                                  │
                                                  ▼
                                             RULE ENGINE
                                             • Offline CWE / OWASP
                                             • Deterministic Scoring
                                                  │
                                                  ▼
                                            AI EXPLANATION
                                            • Simplified Ollama [FEAT 6]
                                            • 4-State Lifecycle
                                            • Sensitive Data Masking
                                                  │
                                                  ▼
                                             REMEDIATION
                                             • Primary Fix + Alternatives
                                                  │
                                                  ▼
                                             AUDIT TRAIL
                                             • Cryptographic Log Entry
                                                  │
                ┌─────────────────────────────────┴─────────────────────────────────┐
                ▼                                                                   ▼
       INDUSTRIAL SECURITY [FEAT 9]                                      PWA & EXTENSION [FEAT 7, 8]
       • IT Network                                                      • Progressive Web App
       • DMZ Architecture                                                • Service Worker Offline Cache
       • OT Network (Modbus / DNP3)                                      • Chrome Extension Companion
       • Honest Statuses (LIVE, DEMO, SIMULATED)                           (1-click tab security assessment)
```

---

## 4. Feature-by-Feature Integration Plan

### Feature 1: Suspicious Malware / Trojan Indicators
- **Integration Layer**: `Detection Engine` $\rightarrow$ `file_scanner.py` & `process_scanner.py`
- **Technical Capabilities**:
  - Double extension detection (e.g., `*.pdf.exe`, `*.docx.vbs`, `*.xlsx.ps1`).
  - Anomalous execution paths: binaries running from `%TEMP%`, `%APPDATA%`, `C:\Users\Public\`, or `\Downloads\`.
  - Process masquerading / spoofing (e.g., `svch0st.exe`, `lsasss.exe`, `csrsss.exe`).
  - Known test signatures (EICAR / mock Trojan indicators) and abnormal entropy.
- **Evidence & Mapping**:
  - Emits `EvidenceRecord` with SHA-256 hash.
  - Maps to **CWE-506** (Embedded Malicious Code) and **OWASP A08:2021-Software and Data Integrity Failures**.
- **Risk to Existing Code**: **Zero**. Adds inspection heuristics to existing scanner functions without altering signatures.

### Feature 2: Worm-like Behavior Indicators
- **Integration Layer**: `Detection Engine` $\rightarrow$ `network_scanner.py` & `process_scanner.py`
- **Technical Capabilities**:
  - High socket fan-out: single unauthorized process opening $>10$ concurrent connections across local `/24` subnet.
  - Probing well-known worm propagation ports: SMB `445`, NetBIOS `139`, RDP `3389`, Telnet `23`, SSH `22`.
  - Rapid connection churn / scanning behavior.
  - Detection of `autorun.inf` markers or hidden executable drops in removable drive roots.
- **Evidence & Mapping**:
  - Emits `EvidenceRecord` linking PID, remote IP list, destination port, and socket state.
  - Maps to **CWE-799** (Improper Control of Interaction Frequency) and **CWE-284**.
- **Risk to Existing Code**: **Zero**. Non-destructive telemetry read via `psutil` / `netstat`.

### Feature 3: Network Exposure Assessment Including Port 8080
- **Integration Layer**: `Detection Engine` $\rightarrow$ `network_scanner.py` & `system_security_scanner.py`
- **Technical Capabilities**:
  - Specific auditing of **Port 8080** (Alternative HTTP, Tomcat, Jenkins, Spring Boot, proxy services).
  - Binding interface classification: `0.0.0.0` (WAN/All-interfaces exposed - High Risk) vs. `127.0.0.1` (Localhost-only - Controlled).
  - Exposure auditing for other common dev/admin ports: `8000`, `8443`, `5000`, `3000`, `5173`.
  - Detection of unauthenticated HTTP exposure or missing TLS certificates on port 8080.
- **Evidence & Mapping**:
  - Emits `EvidenceRecord` with PID, process name, listening address, and protocol.
  - Maps to **CWE-284** (Improper Access Control) and **OWASP A05:2021-Security Misconfiguration**.
- **Risk to Existing Code**: **Zero**. Extends port analysis dictionaries in `network_scanner.py`.

### Feature 4: URL Security Assessment
- **Integration Layer**: `Assessment Engine` $\rightarrow$ `backend/app/services/url_scanner_service.py` & `backend/app/api/routes/url_check.py`
- **Technical Capabilities**:
  - Non-destructive HTTP & TLS assessment:
    1. HTTPS Availability & HTTP $\rightarrow$ HTTPS 301/308 redirect enforcement.
    2. TLS Certificate metadata: Issuer, Subject, validity dates (`notBefore`, `notAfter`), expiration days remaining, TLS protocol version (TLSv1.2/v1.3), cipher suite.
    3. Security Headers: `Content-Security-Policy` (CSP), `Strict-Transport-Security` (HSTS), `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Frame-Options`.
    4. Cookie security attributes: `Secure`, `HttpOnly`, `SameSite`.
    5. Information disclosure headers: `Server`, `X-Powered-By`.
    6. Redirect chain tracking (up to 5 hops).
    7. Public client-side assets & Subresource Integrity (SRI) checks.
  - Check statuses: `PASS`, `FAIL`, `WARNING`, `NOT AVAILABLE`, `NOT TESTED`, `NEEDS REVIEW`.
  - Dual Evidence: **[ SIMPLE EVIDENCE ]** and **[ TECHNICAL EVIDENCE ]**.
  - Safe reproduction CLI command (`curl -I ...`).
  - Remediation with primary fix and reverse proxy alternative.
- **Risk to Existing Code**: **Zero**. Implemented as a dedicated modular service and route.

### Feature 5: 2–3 Real Working Vulnerability Detections
- **Integration Layer**: `Assessment Engine` & `Detection Engine`
- **The 3 Real Working Detections**:
  1. **Real Detection 1: Missing Strict-Transport-Security (HSTS) & Missing Content-Security-Policy (CSP)**
     - *Trigger*: Live HTTP probe against target domain.
     - *Observation*: Response headers lack `Strict-Transport-Security` and `Content-Security-Policy`.
     - *Impact*: Man-in-the-Middle downgrade vulnerability and cross-site scripting exposure.
     - *Classification*: CWE-693 / OWASP A05:2021.
  2. **Real Detection 2: Insecure Wildcard Cross-Origin Resource Sharing (CORS) Misconfiguration**
     - *Trigger*: Live HTTP `OPTIONS` / preflight probe with `Origin: https://attacker-origin.com`.
     - *Observation*: Server reflects `Access-Control-Allow-Origin: *` or echoes arbitrary Origin header with `Access-Control-Allow-Credentials: true`.
     - *Impact*: Cross-origin data leakage of authenticated sessions.
     - *Classification*: CWE-942 / OWASP A01:2021.
  3. **Real Detection 3: Unprotected WAN-Exposed Listening Service on Port 8080**
     - *Trigger*: Live socket inspection on host or remote TCP probe.
     - *Observation*: Process bound to `0.0.0.0:8080` without encryption or firewall isolation.
     - *Impact*: Unauthorized remote network access and unencrypted administration interface.
     - *Classification*: CWE-284 / OWASP A05:2021.
- **Risk to Existing Code**: **Zero**. Fully grounded in real observations and SHA-256 evidence.

### Feature 6: Simplified Ollama Integration
- **Integration Layer**: `AI Explanation Engine` $\rightarrow$ `backend/app/services/ollama_service.py` & `ai_analysis_service.py`
- **Technical Capabilities**:
  - Centralized model configuration via `AI/config.json`.
  - 4-State Lifecycle: 🟢 `AI READY`, 🟡 `AI STARTING`, 🟠 `MODEL UNAVAILABLE`, 🔴 `AI OFFLINE`.
  - Transparent auto-start of local `ollama serve` process.
  - Sensitive data masking: AWS keys, DB passwords, bearer tokens, Slack webhooks, and private keys scrubbed before LLM dispatch.
  - Standardized 7-section output (`WHAT WAS FOUND`, `WHERE`, `WHY IT MATTERS`, `POSSIBLE IMPACT`, `RECOMMENDED ACTION`, `HOW TO FIX`, `HOW TO VERIFY`).
  - 100% deterministic rule-based fallback when AI is offline.
- **Risk to Existing Code**: **Zero**. Already tested and verified with 7/7 passing unit tests.

### Feature 7: Responsive Web / Progressive Web App (PWA) Support
- **Integration Layer**: `Frontend Shell`
- **Technical Capabilities**:
  - `frontend/public/manifest.json`: Defines PWA identity, standalone display mode, theme colors, and icons.
  - `frontend/public/sw.js`: Service worker implementing stale-while-revalidate caching for offline UI shell and critical static assets.
  - Service worker registration in `frontend/index.html`.
  - Responsive layout adaptations: desktop wide-screen $\leftrightarrow$ laptop $\leftrightarrow$ tablet $\leftrightarrow$ mobile bottom navigation bar.
- **Risk to Existing Code**: **Zero**. Purely additive web manifest and service worker.

### Feature 8: Chrome Extension Companion
- **Integration Layer**: Standalone companion directory `extension/`
- **Technical Capabilities**:
  - Manifest V3 compliant extension (`extension/manifest.json`).
  - Popup interface (`popup.html`, `popup.js`, `popup.css`):
    - Reads active browser tab URL.
    - Inspects HTTPS protocol, client cookies, and obvious security headers directly in the browser.
    - Provides a single-click button: **[ Send to KAVACH Assessment ]** that dispatches the URL to `http://localhost:8000/api/url-check/scan`.
    - Displays real-time assessment results and security score within the extension popup.
- **Risk to Existing Code**: **Zero**. Exists in independent `extension/` folder and calls standard KAVACH API.

### Feature 9: Industrial Security (IT/OT Section)
- **Integration Layer**: `Operations Hub` $\rightarrow$ `backend/app/services/industrial_service.py`, `backend/app/api/routes/industrial.py`, `IndustrialSecurityPage.tsx`
- **Technical Capabilities**:
  - Network Architecture Topology: `IT NETWORK ──> DMZ ──> OT NETWORK ──> INDUSTRIAL SYSTEMS`.
  - Environment inspection tabs:
    - `1. IT Environment`: Corporate workstations, enterprise web servers, SQL databases.
    - `2. OT Environment`: SCADA servers, HMIs, Historians, PLCs, RTUs running Modbus/TCP, DNP3, S7comm, OPC UA.
    - `3. IT/OT Demo & Threats`: Simulated industrial threats (unauthorized Modbus coil writing, DMZ firewall jump host bypass, stale engineering workstation credentials).
  - Honest status labeling: `LIVE`, `DEMO`, `SIMULATED`, `NOT CONNECTED`.
- **Risk to Existing Code**: **Zero**. Moves IT/OT functionality into a dedicated sub-view under Operations without disturbing primary World Monitor workflows.

---

## 5. File Modification & Creation Matrix

### 5.1 Existing Files to Modify
| File Path | Nature of Modification | Breaking Risk |
|---|---|---|
| `backend/app/scanners/file_scanner.py` | Add Trojan double-extension and suspicious path heuristics. | **None** (additive logic) |
| `backend/app/scanners/process_scanner.py` | Add process masquerading and abnormal execution path checks. | **None** (additive logic) |
| `backend/app/scanners/network_scanner.py` | Add Port 8080 exposure check and worm fan-out connection heuristics. | **None** (additive logic) |
| `backend/app/api/api.py` | Register `url_check.router` and `industrial.router`. | **None** (router inclusion) |
| `frontend/src/types/index.ts` | Add TypeScript interfaces for URL Security Check and Industrial Security. | **None** (type definitions) |
| `frontend/src/services/api.ts` | Add client methods for `url-check` and `industrial` endpoints. | **None** (additive methods) |
| `frontend/src/App.tsx` | Register routes for URL Check and Industrial Security views. | **None** (switch-case addition) |
| `frontend/index.html` | Register PWA service worker and manifest link. | **None** (additive headers) |

### 5.2 New Files to Create
| File Path | Purpose |
|---|---|
| `backend/app/services/url_scanner_service.py` | Core engine for safe HTTP/TLS URL security checks. |
| `backend/app/api/routes/url_check.py` | REST API routes for URL check execution and re-verification. |
| `backend/app/services/industrial_service.py` | Industrial IT/OT topology, protocol models, and threat simulations. |
| `backend/app/api/routes/industrial.py` | REST API routes for IT/OT environment inspection and simulation. |
| `frontend/src/pages/UrlSecurityCheckPage.tsx` | Minimal, high-clarity URL security check interface. |
| `frontend/src/pages/IndustrialSecurityPage.tsx` | Dedicated IT/OT topology visualization and threat scenario dashboard. |
| `frontend/public/manifest.json` | Web App Manifest for PWA installation. |
| `frontend/public/sw.js` | Progressive Web App Service Worker for offline shell caching. |
| `extension/manifest.json` | Manifest V3 configuration for KAVACH Chrome Extension. |
| `extension/popup.html` | Chrome Extension UI popup. |
| `extension/popup.js` | Chrome Extension active tab inspector and KAVACH API bridge. |
| `extension/popup.css` | Minimal Apple-inspired extension styling. |
| `backend/tests/test_url_security_check.py` | Automated unit tests for URL assessment engine. |
| `backend/tests/test_malware_indicators.py` | Automated unit tests for Trojan and worm heuristics. |

---

## 6. Risk Assessment & Safety Assurances

| Potential Risk | Severity | Mitigation Strategy |
|---|---|---|
| **Breaking Existing Scanners** | Low | Existing scanner function signatures (`scan_processes()`, `scan_network()`, etc.) remain identical; new checks are integrated as additive heuristic passes. |
| **Breaking API Endpoints** | Low | No existing endpoints are modified or deleted; new features use dedicated `/api/url-check` and `/api/industrial` namespaces. |
| **Database Schema Corruption** | None | Existing SQLite database schemas (`assessments`, `findings`, `evidence_records`, `audit_events`) are reused directly without modifying columns. |
| **False Vulnerability Claims** | None | Real checks return honest statuses (`PASS`, `FAIL`, `WARNING`, `NOT TESTED`, `NOT AVAILABLE`); industrial section strictly labels data as `SIMULATED` or `DEMO`. |
| **PWA / Service Worker Conflicts** | Low | Service worker uses standard stale-while-revalidate for static assets only; all `/api/*` network requests bypass service worker cache. |

---

## 7. Approval & Next Steps

This plan strictly preserves all existing functionality, adheres to KAVACH's evidence-first golden rule, and integrates the 9 requested features cleanly. Upon user approval, execution will proceed in phased order:
1. Detection engine heuristic extensions (Trojan, worm, port 8080).
2. URL security check service and REST routes.
3. 2–3 real working vulnerability detections.
4. Industrial IT/OT backend service and routes.
5. Frontend UI views (URL Security Check, Industrial Security).
6. PWA manifest and service worker.
7. Chrome extension companion.
8. Automated tests and verification.
