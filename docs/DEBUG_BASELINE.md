# KAVACH 6.0 — Comprehensive Debug & Baseline Audit Report
**Execution Date**: 2026-09-22 | **Time**: Indian Standard Time (IST)  
**System Profile**: Windows 11 / Python 3.11.9 / PySide6 / React + TypeScript + Vite / SQLite

---

## 1. Application Entry Points

| Subsystem | Entry Point Path | Tech Stack / Architecture | Notes |
|---|---|---|---|
| **Web Backend** | `backend/app/main.py` | FastAPI + Uvicorn + SQLAlchemy | Runs on `http://127.0.0.1:8000`, exposes OpenAPI docs, CORS, WebSocket, and REST API |
| **Web Frontend** | `frontend/src/main.tsx` | React 18 + TypeScript + Vite + Tailwind/Glassmorphism | Runs on `http://127.0.0.1:5173`, full multi-page dashboard |
| **Desktop Client** | `main.py` | PySide6 (Qt) + Dark Glassmorphic Design | Sovereign desktop client with 14 navigation screens |
| **Portable Launcher** | `portable/kavach_portable.py` | PySide6 standalone executable entry | Consent-based portable USB security assessment |
| **Universal Launcher** | `scripts/launch_kavach.py` | Python launcher | Orchestrates backend + frontend + optional desktop client |
| **SIH Full Demo Runner** | `scripts/run_enterprise_demo.py` | Python automated scenario runner | Executes 17-step end-to-end SIH evaluation script |

---

## 2. Important Modules & Subsystems

1. **Assessment Engine** (`backend/app/services/assessment_service.py`, `backend/app/services/world_monitor_assessment_engine.py`, `core/assessment_engine.py`):
   - Handles target validation, scope authorization guard, domain coverage, runtime/source/hybrid assessment modes.
2. **Scanner Modules** (`backend/app/scanners/`):
   - `file_scanner.py`: SHA-256 integrity, hardcoded secrets detection, double-extension anomalies.
   - `process_scanner.py`: Process execution paths, unquoted service paths.
   - `software_scanner.py`: Installed software inventory, CVE correlation.
   - `startup_scanner.py`: Autorun entries, persistence checks.
   - `network_scanner.py`: Listening ports, 0.0.0.0 bind audits.
   - `system_security_scanner.py`: UAC, Windows Firewall, Defender posture checks.
   - `permissions_manager.py`: Granular 6-category user consent boundary enforcement.
3. **URL Scanner Service** (`backend/app/services/url_scanner_service.py`):
   - 7 web security domains, live probe engine, SSL/TLS, Security Headers, CORS, Cookies, Info Disclosure.
4. **Evidence Engine** (`backend/app/services/evidence_service.py`, `backend/app/models/models.py`):
   - Structured 5-point evidence, SHA-256 integrity hash manifest, before/after evidence linking.
5. **Re-Verification / Retest Engine** (`backend/app/services/url_scanner_service.py`, `backend/app/services/remediation_service.py`):
   - Real re-test execution, Before vs After evidence diffing, deterministic status transition (`STILL_OPEN`, `VERIFIED_REMEDIATED`, `UNABLE_TO_VERIFY`).
6. **Risk & CVSS Engine** (`backend/app/services/risk_service.py`, `core/risk_engine.py`):
   - CVSS v3.1 vector calculation, contextual risk prioritization, business impact formula.
7. **Audit Trail Engine** (`backend/app/core/audit.py`, `backend/app/models/models.py`):
   - Cryptographic immutable chained event ledger (SHA-256 linking prev_hash -> current_hash).
8. **RAG & Ollama AI Engine** (`backend/app/rag/`, `backend/app/services/ai_analysis_service.py`, `backend/app/services/ollama_service.py`):
   - Local AI analysis with 5-point deterministic fallback when Ollama is offline.
   - Centralized model configuration via `AI/config.json`.
9. **Forensic Export Engine** (`backend/app/services/forensic_export_service.py`):
   - SHA-256 signed JSON/HTML forensic dossiers.
10. **Report Engine** (`backend/app/services/report_service.py`):
    - Executive summary, technical vulnerability inventory, re-test timeline, audit ledger export.

---

## 3. Important Services & API Surface

- `GET /health` & `GET /api/system/status`: Overall system health and Ollama detection.
- `POST /api/url-check/scan`: Real-time URL assessment.
- `POST /api/url-check/re-verify`: Automated live target re-verification.
- `GET /api/findings` & `GET /api/findings/{id}`: Vulnerability findings retrieval.
- `GET /api/evidence` & `GET /api/evidence/{id}`: Cryptographic evidence chain inspection.
- `POST /api/assessments`: New assessment initialization with authorization enforcement.
- `POST /api/assessments/{id}/retest`: Finding re-test workflow execution.
- `GET /api/world-monitor/status`: Situational telemetry and geographic node posture.
- `POST /api/portable/scan`: Consent-guarded local system scan.
- `GET /api/portable/permissions` & `POST /api/portable/permissions`: Permissions dashboard.
- `POST /api/ai/explain`: RAG + Ollama AI root cause analysis with structured fallback.
- `GET /api/forensic/export/{id}`: Forensic archive creation.
- `GET /api/reports/{id}/html` & `GET /api/reports/{id}/json`: Official assessment reporting.

---

## 4. Database Architecture

- **Engine**: SQLite via SQLAlchemy ORM (`kavach.db`).
- **Core Tables**:
  - `assessments`: Primary assessment runs and metadata.
  - `findings`: Identified security vulnerabilities, CVSS score, priority, status.
  - `evidence`: Cryptographic evidence records, raw observations, SHA-256 hash.
  - `re_verifications`: Before/after re-test comparative audits and state diffs.
  - `audit_events`: Hash-chained immutable audit ledger.
  - `discovery_items`: Discovered endpoints and assets.
  - `experience_items`: Team knowledge base records.
  - `team_members` & `team_assignments`: Sovereign team collaboration records.

---

## 5. Test & Demo Commands

| Scope | Command | Description |
|---|---|---|
| **Backend Unit & Integration Suite** | `python -m pytest backend/tests/ -v` | Runs all 111 backend tests |
| **Scanner Test Suite** | `python test_scanner_suite.py` | Runs 8 automated local scanner tests |
| **Desktop App Smoke Test** | `python test_desktop_app.py` | Validates PySide6 14-page UI initialization |
| **Frontend Production Build** | `npm --prefix frontend run build` | Compiles TypeScript and builds Vite bundle |
| **SIH Full Demonstration** | `python scripts/run_enterprise_demo.py` | 17-step end-to-end automated demo |

---

## 6. Current Baseline Test Results

- **Backend PyTest Suite**: **111 Passed / 0 Failed (100% Pass Rate)**
- **Scanner Suite**: **8/8 Passed (100% Pass Rate)**
- **Frontend Build**: **1890 modules transformed, 0 TypeScript errors, build succeeded**
- **Warnings Detected**:
  1. `schemas.py`: 6 Pydantic V2 deprecation warnings (`class Config` -> `model_config = ConfigDict(...)`).
  2. `url_check.py`: `Field(..., example=...)` deprecated in Pydantic V2 (`json_schema_extra` preferred).
  3. `portable.py`: `p.dict()` deprecated in Pydantic V2 (`p.model_dump()` preferred).

---

## 7. Suspected Dead Code & Unnecessary Files

1. **Large Obsolete Root Artifacts**:
   - `.pytest_cache.zip` (448 MB) — Old temporary compressed pytest cache in root.
   - `.zip` (224 MB) — Unreferenced root zip artifact.
   - `..KAVACH_COMPLETE_PROJECT.md` (37 MB) — Root duplicate of `INFO/KAVACH_COMPLETE_PROJECT.md`.
2. **Duplicate Code / Wrappers to Audit**:
   - `core/risk_engine.py` vs `backend/app/services/risk_service.py` & `backend/app/services/risk_engine.py`.
   - `core/target_config.py` vs `backend/app/core/target_config.py`.
   - `services/storage_service.py` & `services/ollama_service.py` vs `backend/app/services/...`.
3. **Pydantic V1/V2 Syntax Hygiene**:
   - Modernize `class Config` across schemas to eliminate all 19 pytest deprecation warnings.
